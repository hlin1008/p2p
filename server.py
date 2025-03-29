import socket
import threading
import json
import uuid

# Define basic HOST/PORT parameters
HOST = '0.0.0.0'
PORT = 65433

# For now, saving client info in a list of dicts. Switching to SQLite later.
# Specifically, this should only be for online clients
CLIENTS = []


# Initiate Server Socket and Start Listening
print("[STARTING] Server is starting...")
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen()


def get_available_clients(client_id):
    """
    Function that takes in id of a client, returns a list of available clients(without self).

    Input: 
        client_name: str, name of client 
    Output: 
        available_clients: list, a list of dictionary of available client's info
    """
    available_clients = []
    for client in CLIENTS:
        if client["name"] != client_name:
            available_clients.append({"name": client["name"], 
                                      "addr": addr})
    return available_clients



# While-Loop that appends client data when new connection established
# Also send available clients when connection established 
while True:
    conn, addr = server.accept()

    # Receiving New User Data
    client_name = conn.recv(1024).decode("utf-8")
    print(f"[NEW CONNECTION] {addr} connected.")
    client_id = str(uuid.uuid4())
    client_info = {"id": client_id,
                   "name": client_name,
                   "addr": addr,
                   "conn": conn}
    


    CLIENTS.append(client_info)

    # Sending Available Client Data to New User
    available_clients = get_available_clients(client_id)
    conn.send(json.dumps({"type": "user_list",
                          "users": available_clients}).encode("utf-8"))


    
# CLIENTS[client_id] = []
