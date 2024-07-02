import socket
import os

def handle_client(client_socket):
    
    client_socket.close()

def start_server(port):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('localhost', port))
    server.listen(3)

    print(f"Server is listening on port {port}...")

    while True:
        client_socket, _ = server.accept()
        handle_client(client_socket)

if __name__ == "__main__":
    start_server(int(os.getenv('PORT')))