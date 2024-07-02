import socket

from config import AVAILABLE_SERVER_NODES, BUFFER_MAX_SIZE, MIDDLEWARE_PORT, MIDDLEWARE_HOST

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
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((main_host, main_port))
        with client:
            while True:
                data_chunk = client_socket.recv(1024)
                if not data_chunk:
                    break
            # send file?

    except Exception as e:
        print('Error while handling the client request.', e)

def main():
    manager = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    manager.bind((MIDDLEWARE_HOST, MIDDLEWARE_PORT))
    manager.listen(3)

    print(f"Middleware is listening on port {MIDDLEWARE_PORT}...")

    while True:
        client_socket, addr = manager.accept()

        print("connection stablished with port", addr)

        handle_client(client_socket)
        client_socket.close()

if __name__ == "__main__":
    main()