import socket
import threading

# Define basic HOST/PORT parameters
HOST = '0.0.0.0'
PORT = 65433

# Define Server Socket and Start Listening
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen()

# Keep track of clients
clients = []

# Handle Client - late could be changed to CRUD of clients
def handle_client(conn, addr):
    print(f"[NEW CONNECTION] {addr} connected.")
    while True:
        try:
            msg = conn.recv(1024).decode('utf-8')
            if msg:
                print(f"[{addr}] {msg}")
                broadcast(msg, conn)
        except:
            clients.remove(conn)
            conn.close()
            break

# Show broadcast to
def broadcast(message, sender_conn):
    for client in clients:
        if client != sender_conn:
            client.send(message.encode('utf-8'))

print("[STARTING] Server is starting...")
while True:
    conn, addr = server.accept()
    clients.append(conn)
    thread = threading.Thread(target=handle_client, args=(conn, addr))
    thread.start()