import socket
import threading
import json
import uuid

# Define basic HOST/PORT parameters
HOST = '0.0.0.0'
PORT = 65431

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
    Appends new user data, sends available client list to user, initiates listening.

    Inputs:
        conn: socket, connection of new client's socket
        addr: address of the client
    Outputs:
        N/A
    """
    # Receiving New User Data
    client_name_and_p2p = conn.recv(1024).decode("utf-8")
    client_name_and_p2p = json.loads(client_name_and_p2p)
    client_name = client_name_and_p2p["name"]
    client_p2p_port = client_name_and_p2p["p2p_port"]
    client_p2p_host = client_name_and_p2p["p2p_host"]
    print(f"[NEW CONNECTION] {client_name} at {addr} connected.")
    client_id = str(uuid.uuid4())
    client_info = {"client_id": client_id,
                   "name": client_name,
                   "addr": addr,
                   "conn": conn,
                   "p2p_host": client_p2p_host,
                   "p2p_port": client_p2p_port}

    CLIENTS.append(client_info)

    # Sending Available Client Data to New User
    available_clients = get_available_clients(client_id)
    client_info = filter_client_info(client_info)

    conn.send(json.dumps({"type": "user_list",
                          "users": available_clients,
                          "client_info": client_info}).encode("utf-8"))
    
    # Start lisening to incoming request from client
    listen_to_client(conn, client_info)

def get_available_clients(client_id):
    """
    Function that takes in id of a client, returns a list of available clients(without self).

    Input: 
        client_id: string, the id of the client that is requesting available clients
    Output: 
        available_clients: list, a list of dictionary of available client's info
    """
    available_clients = []
    for client in CLIENTS:
        if client["client_id"] != client_id:
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
            "client_id": client_info["client_id"],
            "p2p_host": client_info["p2p_host"],
            "p2p_port": client_info["p2p_port"]}


def listen_to_client(conn: socket.socket, client_from_info:dict):
    while True:
        try:
            msg = conn.recv(1024).decode("utf-8")
            msg = json.loads(msg)
            client_from_name = client_from_info['name']

            if msg["type"] == "chat_request":
                client_to_name = msg["client_to"]["name"]
                print(f"[P2P CHAT REQUEST] {client_from_name} requested to chat with {client_to_name}")
                process_chat_request(client_from_info, msg)

            elif msg["type"] == "chat_request_response":
                process_cr_response(msg)
                
            else:
                print("[UNKNOWN MESSAGE]", msg)

        except:
            print(f"[DISCONNECTED] {client_from_info['name']}")
            for c in CLIENTS:
                if c["client_id"] == client_from_info["client_id"]:
                    # Remove the client from the list of clients
                    CLIENTS.remove(c)
            conn.close()
            break

def process_chat_request(client_from_info: dict, request_message):
    """
    Helper function that processes chat_request from conn to client specified in the 
    request_message.

    Inputs:
        client_from_info: dictionary, contains client info of the requesting client
        request_message: dictionary, contains chat_request message
    Outputs:
        N/A
    """
    id_client_to = request_message["client_to"]["client_id"]

    # Find the connection of the client that is being requested to
    # and send the request message to them
    for c in CLIENTS:
        if id_client_to == c["client_id"]:
            conn_client_to = c["conn"]

    filtered_client_from_info = filter_client_info(client_from_info)
    chat_request = {"type": "chat_request",
                    "client_from": filtered_client_from_info}
    chat_request = json.dumps(chat_request)
    chat_request_encoded = chat_request.encode("utf-8")
    conn_client_to.send(chat_request_encoded) 

def process_cr_response(response_message):
    """
    Helper function that processes chat_request_response from conn to client specified in the
    request_message.
    Inputs:
        response_message: dictionary, contains chat_request_response message
    Outputs:
        N/A
    """
    client_to_name = response_message["client_to"]["name"]
    client_from_name = response_message["client_from"]["name"]
    status = response_message["status"]
    print(f"[P2P CHAT REQUEST RESPONSE] {client_from_name} {status} to chat request from {client_to_name}")




# While-Loop that appends client data when new connection established
# Also send available clients when connection established 
while True:
    conn, addr = server.accept()
    threading.Thread(target=handle_new_client, args=(conn, addr)).start()
    
 