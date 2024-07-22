import sqlite3
import socket
import threading
import re

from config import INDEXER_PORT, ONE_KILOBYTE

def initialize(connection: sqlite3.Connection):
    connection.execute('''CREATE TABLE IF NOT EXISTS files (
                    id INTEGER PRIMARY KEY, 
                    name VARCHAR(255), 
                    server_instance VARCHAR(255), 
                    replica_instance VARCHAR(255))
                 ''')

def insert_index(connection: sqlite3.Connection, file_name, server_instance, replica_instance):
    sql = '''INSERT INTO files (name, server_instance, replica_instance)
                                VALUES (?, ?, ?)'''
    cursor = connection.cursor()
    cursor.execute(sql, (file_name, server_instance, replica_instance))
    
    connection.commit()

    print(f'[+] Successfuly inserted the indexed file in the database with id: {cursor.lastrowid}')

def get_indexed_files(connection: sqlite3.Connection):  
    data = connection.execute('SELECT * FROM files')
    return data.fetchall()

def get_indexed_file_by_name(connection: sqlite3.Connection, name: str, server: str):  
    data = connection.execute(f"SELECT * FROM files 
                                WHERE name LIKE '%{name}%'
                                AND server_instance LIKE '%{server}%'
                                ORDER BY id DESC")
    return data.fetchone()


def increment_version(file_name):
    pattern = r'\(\s*(\d+)\s*\)'

    match = re.search(pattern, file_name)

    if match:
        current_version = int(match.group(1))
        new_version = current_version + 1
        new_file_name = re.sub(pattern, f'({new_version})', file_name)
    else:
        base_name, ext = re.splitext(file_name)
        new_file_name = f"{base_name} (1){ext}"

    return new_file_name
    
def handle_client(client_socket: socket.socket):
    connection = sqlite3.connect('database.db')

    header = client_socket.recv(ONE_KILOBYTE).decode()
    
    filename, server_host, replica_host = header.split('_')

    print(f"[*] received the metadata for the file: {filename}")

    existing_file = get_indexed_file_by_name(connection, filename, server_host)

    if existing_file:
        new_filename = increment_version(existing_file[1])

        print('existing file', existing_file)
        print('version', new_filename)

        insert_index(connection, new_filename, server_host, replica_host)
    else:
        insert_index(connection, filename, server_host, replica_host)

    connection.close()


def main():
    indexer = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    indexer.bind((socket.gethostname(), INDEXER_PORT))
    indexer.listen(3)

    print(f"[*] Indexer is listening on port {INDEXER_PORT}...")

    connection = sqlite3.connect('database.db')
    initialize(connection)

    saved_files = get_indexed_files(connection)

    if len(saved_files) == 0:
        print(f"[*] There are no saved files in the server!")
    else:
        print(f"[*] List of saved files: ")
        for f in saved_files:
            print(f"[*] File: {f[1]}, server instance: {f[2]}, replica instance: {f[3]}")

    connection.close()

    while True:
        client_socket, addr = indexer.accept()

        print("[*] Connection stablished with ", addr)

        thread = threading.Thread(target=handle_client, args=(client_socket,))
        thread.start()

if __name__ == '__main__':
    main()