import socket
import os
import threading

from config import ONE_KILOBYTE, END_BYTE_STRING

def handle_client(client_socket: socket.socket):
    header = client_socket.recv(ONE_KILOBYTE).decode().strip()

    if not header: return

    file_name, file_size, replica_host, replica_port = header.split(':')
    file_size = int(file_size)
    file_data = b""

    print(f"[*] received the file {file_name} with a size of {file_size}")
    print(f"[*] Selected replica - HOST: {replica_host or ''} PORT: {replica_port or ''}")

    while True:
        data_chunk = client_socket.recv(ONE_KILOBYTE)
        if file_data[-5:] == END_BYTE_STRING:
            break
        file_data += data_chunk

    file_data = file_data[:-5]

    with open(file_name, 'wb+') as f:
        f.write(file_data)

    client_socket.close()

    if (replica_host and replica_port):
        header = f"{file_name}:{file_size}::".ljust(ONE_KILOBYTE)
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((replica_host, int(replica_port)))

        client.sendall(header.encode())
        client.sendall(file_data)
        client.send(END_BYTE_STRING)
        client.close()

def start_server(port):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((socket.gethostname(), port))
    server.listen(3)

    print(f"[*] Server is listening on port {port}...")

    while True:
        client_socket, addr = server.accept()
        
        # print("[*] Connection stablished with ", addr)

        thread = threading.Thread(target=handle_client, args=(client_socket,))
        thread.start()

if __name__ == "__main__":
    start_server(int(os.getenv('PORT')))