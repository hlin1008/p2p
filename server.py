import socket
import threading
import json
import uuid

# Define basic HOST/PORT parameters
HOST = '0.0.0.0'
PORT = 65435

# For now, saving client info in a list of dicts. Switching to SQLite later.
# Specifically, this should only be for online clients
CLIENTS = []


# Initiate Server Socket and Start Listening
print("[STARTING] Server is starting...")
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen()


def handle_new_client(conn, addr):
    """
    Helper function that handles a newly connected client. 
    Appends new user data, sends available clinet list to user, initiates listening.

    Inputs:
        conn: socket, connection of new client's socket
        addr: address of the client
    Outputs:
        N/A
    """


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
    
    # Start lisening to incoming request from client
    listen_to_client(conn, client_info)

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
        if client["id"] != client_id:
            filtered_info = filter_client_info(client)
            available_clients.append(filtered_info)
    return available_clients

def filter_client_info(client_info:dict):
    """
    Helper function that extracts data from server end client info data that could be sent to client end.

    Input:
        client_info: dictionary, contains all server end data
    Output:
        filtered_client_info: dictionary, contains sendable client end data
    """
    return {"name": client_info["name"],
            "client_id": client_info["id"]}


def listen_to_client(conn, client_from_info:dict):
    while True:
        try:
            req_msg = conn.recv(1024).decode("utf-8")
            req_msg = json.loads(req_msg)
            client_from_name = client_from_info['name']
            client_to_name = req_msg["client_to"]["name"]
            print(f"[P2P CHAT REQUEST] {client_from_name} requested to chat with {client_to_name}")
            print(req_msg)
            if req_msg["type"] == "chat_request":
                process_chat_request(client_from_info, req_msg)
            else:
                print(req_msg)
            # could add block_user and other stuff later on
        except:
            print(f"[DISCONNECTED] {client_from_info['name']}")
            CLIENTS.remove(client_from_info)
            conn.close()
            break


def process_chat_request(client_from_info: dict, request_message):
    """
    Helper function that processes chat_request from conn to client specified in the 
    request_message.
    """
    id_client_to = request_message["client_to"]["client_id"]
    print(id_client_to)
    for c in CLIENTS:
        if id_client_to == c["id"]:
            conn_client_to = c["conn"]

    filtered_client_from_info = filter_client_info(client_from_info)
    chat_request = {"type": "chat_request",
                    "client_from": filtered_client_from_info}
    chat_request = json.dumps(chat_request)
    chat_request_encoded = chat_request.encode("utf-8")
    conn_client_to.send(chat_request_encoded) 
    







# While-Loop that appends client data when new connection established
# Also send available clients when connection established 
while True:
    conn, addr = server.accept()
    threading.Thread(target=handle_new_client, args=(conn, addr)).start()
    


    
# CLIENTS[client_id] = []
