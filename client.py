import socket
import os

from config import MIDDLEWARE_HOST, MIDDLEWARE_PORT

def start_client():
    while True:
        file_path = input("Enter the path to the file to backup: ")

        if os.path.isfile(file_path):
            middleware_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            middleware_client.connect((MIDDLEWARE_HOST, MIDDLEWARE_PORT))

            # sending the file in chunks
            with open(file_path, 'rb') as f:
                file_bytes = f.read()
                middleware_client.sendall(file_bytes)

            middleware_client.close()
        else:
            print("File not found. Please try again.")

if __name__ == "__main__":
    start_client()