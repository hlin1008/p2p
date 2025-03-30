import socket
import threading
import json
import random

# Define basic HOST/PORT parameters
HOST = '0.0.0.0'
PORT = 65435

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


# Do input for client for now, change it to methods like drop list later

"""peer_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
peer_host = '0.0.0.0'
peer_port = random.randint(62000, 65000)  # change later to take out random
peer_server.bind((HOST, PORT))
peer_server.listen()"""

def client_side_server(client_from, client_to):
    """
    Function that sets up a server for client_from to talk to client_to
    Input: 
        client_from, client_to: client names
    Output
    """
    pass


    

def receive_chat_request(chat_request_msg):
    """
    Helper function of receive() that processes chat requests on the client end.

    Input: 

    Output:
    """
    client_from_name = chat_request_msg["client_from"]["name"]
    print(f"{client_from_name} sent you a chat request. Accept?[y/n]")
    accepted_request = input()

    if accepted_request == "Y":
        acceptance_msg = json.dumps({"type": "chat_request_response", "status": "accepted"})
        client.send(acceptance_msg.encode("utf-8"))
    else:
        rejection_msg = json.dumps({"type": "chat_request_response", "status": "rejected"})
        client.send(rejection_msg.encode("utf-8"))

def receive_cr_response(conn, cr_response_msg):
    """
    Helper Function of receive() that processes chat request response.
    """
    if cr_response_msg["status"] == "accepted":
        # INITIATE SERVER AND SEND PORT CONNECTION DETAILS
        pass
    elif cr_response_msg["status"] == "rejected":
        pass

def receive_text(conn, cr_response_msg):
    """
    Helper Function of receive() that processes text. 

    input:

    Output:

    """
    pass


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
                receive_cr_response()
            elif msg["type"] == "chat":
                receive_text(msg)
            
        except:
            print("Disconnected from server from receiving chat request.")
            break

"""def receive_cr_response():

    while True:
        try:
            chat_request_msg = json.loads(client.recv(1024).decode('utf-8'))
            client_from_name = chat_request_msg["client_from"]["name"]
            print(f"{client_from_name} sent you a chat request. Accept?[y/n]")
            accepted_request = input()

            if accepted_request == "Y":
                acceptance_msg = json.dumps({"type": "chat_request_response", "status": "accepted"})
                client.send(acceptance_msg.encode("utf-8"))
            else:
                rejection_msg = json.dumps({"type": "chat_request_response", "status": "rejected"})
                client.send(rejection_msg.encode("utf-8"))
        except:
            print("Disconnected from server from receiving chat request.")
            break"""


def send_chat_request():
    """
    Function that sends chat invite to another client that current client wants to chat to.

    Input: 
        client_to: python dictionary, contains all client info
    """
    while True:
        try:
            client_to_name = input("Who would you like to talk to?")

            for c in client_list:
                if c["name"] == client_to_name:
                    client_to = c
            chat_request = json.dumps({"type": "chat_request","client_to": client_to}).encode("utf-8")
            client.send(chat_request)
        except:
            break

def send_chat(client_to):
    """
    Function that sends chat message to another client.
    """
    

def send():
    """
    Function to receive message
    """
    while True:
        msg = input()
        msg = f"{username}: " + msg
        client.send(msg.encode('utf-8'))

# Threads for sending and receiving
threading.Thread(target=send_chat_request).start()
threading.Thread(target=receive).start()

