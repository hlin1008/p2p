import socket
import threading
import json
import random

# Define basic HOST/PORT parameters
HOST = '0.0.0.0'
PORT = 65433

# Get Username, Initiate client Socket and establish Connection
username = input("Enter name: ")
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((HOST, PORT))
client.send(username.encode("utf-8"))

# Server end has send info of currently available clients
client_list = json.loads(client.recv(1024).decode("utf-8"))
if client_list["type"] == "user_list":
    print("Online users:", client_list["users"]) # change so that user can only see client name later


# Do input for client for now, change it to methods like drop list later
other_client_name = input("Who would you like to talk to?")

if other_client_name:
    peer_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    peer_host = '0.0.0.0'
    peer_port = random.randint(62000, 65000)  # change later to take out random
    peer_server.bind((HOST, PORT))
    peer_server.listen()

def client_side_server(client_from, client_to):
    """
    Function that sets up a server for client_from to talk to client_to
    Input: 
        client_from, client_to: client names
    Output
    """
    pass

def send_chat_request(client_to: dict):
    """
    Function that sends chat invite to another client that current client wants to chat to.

    Input: 
        client_to: python dictionary, contains all client info
    """
    json.dumps({"type": "chat_request","client_to": client_to}).encode("utf-8")
    client.send(client_to)
    pass

def send_chat(client_to):
    """
    Function that sends chat message to another client.
    """
    
    



def receive():
    """
    Function to send message
    """
    while True:
        try:
            msg = client.recv(1024).decode('utf-8')
            print(f"\n[New Message] {msg}")
        except:
            print("Disconnected from server.")
            break

def send():
    """
    Function to receive message
    """
    while True:
        msg = input()
        msg = f"{username}: " + msg
        client.send(msg.encode('utf-8'))

# Threads for sending and receiving
threading.Thread(target=receive).start()
threading.Thread(target=send).start()
