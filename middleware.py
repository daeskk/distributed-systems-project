import socket
import time
import threading

from config import AVAILABLE_SERVER_NODES, END_BYTE_STRING, MIDDLEWARE_PORT, ONE_KILOBYTE

server_status = {address: False for address in AVAILABLE_SERVER_NODES}
current_server = 0

def check_server_health(server_address):
    try:
        with socket.create_connection(server_address, timeout=1):
            return True
    except (socket.timeout, ConnectionRefusedError):
        return False

def health_check():
    while True:
        for server in AVAILABLE_SERVER_NODES:
            server_status[server] = check_server_health(server)
        time.sleep(10)
        print('[*] Servers status:', server_status)

def send_file(file_data, file_name, file_size, main_host, main_port, replica_host, replica_port):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((main_host, main_port))

    header = f"{file_name}:{file_size}:{replica_host}:{replica_port}".ljust(ONE_KILOBYTE)

    client.sendall(header.encode())
    client.sendall(file_data)
    client.send(END_BYTE_STRING)
    
    client.close()

def load_balance():
    global current_server
    
    healthy_servers = [server for server, status in server_status.items() if status]
    
    if len(healthy_servers) < 2:
        return None, None
    
    primary_server = healthy_servers[current_server % len(healthy_servers)]
    replica_server = healthy_servers[(current_server + 1) % len(healthy_servers)]
    current_server = (current_server + 1) % len(healthy_servers)
    
    return primary_server, replica_server

def handle_client(client_socket: socket.socket):
    main_server, replica_server = load_balance()

    if not main_server or not replica_server:
        client_socket.sendall('No available servers!'.encode())
        return
    
    client_socket.sendall('Available server found!'.encode())
    
    main_host = main_server[0]
    main_port = main_server[1]
    replica_host = replica_server[0]
    replica_port = replica_server[1]


    print(f"[*] Selected host {main_server} and replica {replica_server}")

    try:
        header = client_socket.recv(ONE_KILOBYTE).decode().strip()
        file_name, file_size = header.split(':')
        file_size = int(file_size)
        file_data = b""

        print(f"[+] received the file {file_name} with a size of {file_size}")

        while True:
            data_chunk = client_socket.recv(ONE_KILOBYTE)
            if file_data[-5:] == END_BYTE_STRING:
                break
            file_data += data_chunk

        file_data = file_data[:-5]

        send_file(file_data, 
                  file_name, file_size, 
                  main_host, main_port, 
                  replica_host, replica_port)

    except Exception as e:
        print('[-] Error while handling the client request.', e)

def main():
    manager = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    manager.bind((socket.gethostname(), MIDDLEWARE_PORT))
    manager.listen(3)

    health_check_thread = threading.Thread(target=health_check)
    health_check_thread.daemon = True
    health_check_thread.start()

    print(f"[*] Middleware is listening on port {MIDDLEWARE_PORT}...")

    while True:
        client_socket, addr = manager.accept()

        print("[*] Connection stablished with ", addr)

        handle_client(client_socket)
        client_socket.close()

if __name__ == "__main__":
    main()