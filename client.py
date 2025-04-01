import socket
import threading
import json
import random

# Define basic HOST/PORT parameters
HOST = '0.0.0.0'
PORT = 65431

# Get Username, Initiate client Socket and establish Connection
username = input("Enter name: ")
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((HOST, PORT))
client.send(username.encode("utf-8"))

# Server end has send info of currently available clients - CHANGE LATER SO THAT CLIENT LIST COULD BE UPDATED
client_list_raw = json.loads(client.recv(1024).decode("utf-8"))
if client_list_raw["type"] == "user_list":
    print("Online users:", client_list_raw["users"]) # change so that user can only see client name later
client_list = client_list_raw["users"]
client_info = client_list_raw["client_info"]

# p2p_server_list contains all the servers that are currently running
# p2p_client_list contains all the clients that are connected to other p2p servers
p2p_server_list = {} # elements within would be id: [port, server]
p2p_client_list = {} # elements within would be id: [port, client]

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
                                    "client_id": client_info["id"]})
        client.send(acceptance_msg.encode("utf-8"))

        # If Accepted, also just connect to server from port at chat_request_msg
        p2p_client_port = chat_request_msg["client_port"]
        p2p_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        p2p_client.connect((HOST, p2p_client_port))


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
        client_id = cr_response_msg["client_id"]
        p2p_server = p2p_server_list[client_id][1]
        in_p2p_server = True
        threading.Thread(target=send, args=p2p_server,).start()
    elif cr_response_msg["status"] == "rejected":
        # Removes the client from the list of available clients because they rejected the request
        del client_list[cr_response_msg["client_id"]]

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
        except:
            print("Disconnected from server from receiving chat request.")
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
            p2p_port = random.randint(50001,60000) 
            chat_request = json.dumps({"type": "chat_request", "client_to": client_to, "client_port": p2p_port}).encode("utf-8")

            # starting a p2p server
            p2p_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            p2p_server.bind((HOST, p2p_port))
            p2p_server.listen()

            # saving it to list of ports
            p2p_server_list[client_to["client_id"]] = [p2p_port, p2p_server]

            client.send(chat_request)
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

