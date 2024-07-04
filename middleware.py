import socket
# import tqdm

from config import AVAILABLE_SERVER_NODES, END_BYTE_STRING, MIDDLEWARE_PORT, MIDDLEWARE_HOST, ONE_KILOBYTE

def send_file(file, host, port, replica_host, replica_port):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((host, port))
    
    client.close()

def handle_client(client_socket: socket.socket):
    # TODO: select a server to send the file to be saved
    
    main_server = AVAILABLE_SERVER_NODES[0]
    replica_server = AVAILABLE_SERVER_NODES[1]

    main_host = main_server[0]
    main_port = main_server[1]
    replica_host = replica_server[0]
    replica_port = replica_server[1]

    try:
        header = client_socket.recv(1024).decode()
        file_name, file_size = header.split(':')
        file_size = int(file_size)
        file_data = b""

        print(f"[*] received the file {file_name} with a size of {file_size}")

        while True:
            data_chunk = client_socket.recv(ONE_KILOBYTE)
            if file_data[-5:] == END_BYTE_STRING:
                break
            file_data += data_chunk

        file_data = file_data[:-5]

        

    except Exception as e:
        print('[*] Error while handling the client request.', e)

def main():
    manager = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    manager.bind((MIDDLEWARE_HOST, MIDDLEWARE_PORT))
    manager.listen(3)

    print(f"[*] Middleware is listening on port {MIDDLEWARE_PORT}...")

    while True:
        client_socket, addr = manager.accept()

        print("[*] Connection stablished with ", addr)

        handle_client(client_socket)
        client_socket.close()

if __name__ == "__main__":
    main()