import socket
import threading
import json
import random

# Define basic HOST/PORT parameters
HOST = '0.0.0.0'
PORT = 65432

# Get Username, Initiate client Socket and establish Connection
username = input("Enter name: ")
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((HOST, PORT))
client.send(username.encode("utf-8"))

# Server end has send info of currently available clients - CHANGE LATER SO THAT CLIENT LIST COULD BE UPDATED
client_list_raw = json.loads(client.recv(1024).decode("utf-8"))
if client_list_raw["type"] == "user_list":
    print("Online users:", client_list_raw["users"]) # change so that user can only see client name later
client_list = client_list_raw["users"] # list of all clients
client_info = client_list_raw["client_info"] # info of current client

# for debugging purposes
print("Client list:", client_list)
print("Client info:", client_info)

# Initiates P2P Server Socket
p2p_server_host = '0.0.0.0'
p2p_server_port = random.randint(50001,60000) 
p2p_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
p2p_server.bind((HOST, p2p_server_port))
p2p_server.listen()

# Parameter that sates whether the client is in a p2p server or not
in_p2p_server = False
    

def receive_chat_request(chat_request_msg):
    """
    Helper function of receive() that processes chat requests on the client end. Takes in a chat rq and unwraps it.

    Input: 
        chat_request_msg: dictionary, contains "type", "client_from" -> another dictionary, client's info
    Output:
    """
    client_from_name = chat_request_msg["client_from"]["name"]
    accepted_request = input(f"{client_from_name} sent you a chat request. Accept?[y/n]\n")

    if accepted_request == "y":

        acceptance_msg = json.dumps({"type": "chat_request_response", 
                                     "status": "accepted", 
                                     "client_id": client_info["client_id"]})
        client.send(acceptance_msg.encode("utf-8"))

    else:
        rejection_msg = json.dumps({"type": "chat_request_response", 
                                    "status": "rejected",
                                    "client_id": client_info["id"]})
        client.send(rejection_msg.encode("utf-8"))


def receive_cr_response(cr_response_msg):
    """
    Helper Function of receive() that processes chat request response.
    """
    if cr_response_msg["status"] == "accepted":
        print("Chat request accepted. You can start texting now!")
        in_p2p_server = True
        threading.Thread(target=wait_for_p2p_connection, args=(p2p_server,), daemon=True).start()
        
    elif cr_response_msg["status"] == "rejected":
        pass


def receive_text(text_msg):
    """
    Helper Function of receive() that processes text. 

    input:

    Output:

    """
    text_msg = json.loads(text_msg.decode("utf-8"))
    text_msg = text_msg["msg"]
    print(text_msg)


def receive():
    """
    Function that helps receiving client chat requests.

    Input: 
    """
    while True:
        try:
            msg = json.loads(client.recv(1024).decode('utf-8'))

            if msg["type"] == "chat_request":
                receive_chat_request(msg)
            elif msg["type"] == "cr_response":
                receive_cr_response(msg)
            elif msg["type"] == "chat":
                receive_text(msg)
            elif msg["type"] == "server_broadcast":
                print(msg["msg"])
        except Exception as e:
            print(f"[ERROR] {e}")
            break


def send_chat_request():
    """
    Function that sends chat invite to another client that current client wants to chat to.

    Input: 
        client_to: python dictionary, contains all client info
    """
    while not in_p2p_server:
        try:
            client_to_name = input("Who would you like to talk to?")

            for c in client_list:
                if c["name"] == client_to_name:
                    client_to = c
            chat_request = json.dumps({"type": "chat_request", "client_to": client_to, "client_port": p2p_server_port}).encode("utf-8")
            

            # saving it to list of ports
            p2p_server_list[client_to["client_id"]] = [p2p_port, p2p_server]

            client.send(chat_request)

            print(f"[Starting P2P Server] on port{p2p_port}")
        except:
            break
    

def send(p2p_server):
    """
    Function to receive message
    """
    while True:
        msg = input()
        msg = f"{username}: " + msg
        msg_json = json.dumps({"type": "chat", "msg": msg})
        p2p_server.send(msg_json.encode('utf-8'))


def start_chat(p2p_server):
    """
    Function that starts the chat with the client that accepted the chat request.
    """
    conn, addr = p2p_server.accept()
    print(f"Connected to {addr}")

    while True:
        try:
            msg = conn.recv(1024).decode("utf-8")
            if msg:
                print(msg)
            else:
                break
        except:
            break

# Threads for sending and receiving
threading.Thread(target=send_chat_request).start()
threading.Thread(target=receive).start()

