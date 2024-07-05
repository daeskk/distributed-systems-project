import socket
import os

from config import END_BYTE_STRING, ONE_KILOBYTE, MIDDLEWARE_HOST, MIDDLEWARE_PORT

def start_client():
    while True:
        try:
            file_path = input("Enter the path to the file to backup: ")

            if os.path.isfile(file_path):
                middleware_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                middleware_client.connect((MIDDLEWARE_HOST, MIDDLEWARE_PORT))

                with open(file_path, 'rb') as f:
                    file_name = os.path.basename(file_path)
                    file_size = os.path.getsize(file_path)
                    header = f"{file_name}:{file_size}".ljust(ONE_KILOBYTE)

                    middleware_client.sendall(header.encode())

                    data = f.read()
                    middleware_client.sendall(data)
                    middleware_client.send(END_BYTE_STRING)

                print('[+] File has been sent to the server.')

                middleware_client.close()
            else:
                print("[-] File not found. Please try again.")

        except Exception as e:
            print('[!] An unexpected error occurred:', e)

if __name__ == "__main__":
    start_client()