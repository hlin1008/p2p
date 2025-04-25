import socket
import threading
import json
import random

# Define basic HOST/PORT parameters
HOST = '0.0.0.0'
PORT = 65430

# Initiates P2P Server Socket
p2p_server_host = '0.0.0.0'
p2p_server_port = random.randint(50001,60000) 
p2p_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
p2p_server.bind((HOST, p2p_server_port))
p2p_server.listen()

# Get Username, Initiate client Socket and establish Connection
username = input("Enter name: ")
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((HOST, PORT))
userinfo = {"name": username, "p2p_port": p2p_server_port, "p2p_host": p2p_server_host}
userinfo = json.dumps(userinfo)
client.send(userinfo.encode("utf-8"))

# Create p2p_client socket
p2p_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Server end has send info of currently available clients - CHANGE LATER SO THAT CLIENT LIST COULD BE UPDATED
client_list_raw = json.loads(client.recv(1024).decode("utf-8"))
print("\nOnline Users:")
for user in client_list_raw["users"]:
    if user["name"] != username:
        print(f"- {user['name']}")

client_list = client_list_raw["users"] # list of all clients
client_info_self = client_list_raw["client_info"] # info of current client


def send_chat_request():
    """
    Function that sends chat invite to another client that current client wants to chat to.
    """
    # Get the client that the current client wants to chat to
    client_to_name = input("\nWho would you like to talk to?\n")

    # Check if the client is in the client list
    client_to = None
    for c in client_list:
        if c["name"] == client_to_name:
            client_to = c

    # If entered a client, Fire up the p2p server
    if client_to:
        chat_request = json.dumps({"type": "chat_request", "client_to": client_to, "client_from": client_info_self}).encode("utf-8")
        client.send(chat_request)
        p2p_conn, _ = p2p_server.accept()

        # The first thing the p2p server receives is a should be the chat request response
        status_message = json.loads(p2p_conn.recv(1024).decode("utf-8"))
        if status_message["status"] == "accepted":
            print(f"\nConnected to {client_to_name}!")
            print(f"\n===== Chat with {client_to_name} starts below ===== \n")

        chat_session(p2p_conn)


def chat_session(p2p_socket):
    threading.Thread(target=receive, args=(p2p_socket, )).start()
    while True:
        send(p2p_socket)


def receive_chat_request(chat_request_msg):
    """
    Helper function of receive() that processes chat requests on the client end. Takes in a chat rq and unwraps it.

    Input: 
        chat_request_msg: dictionary, contains "type", "client_from" -> another dictionary, client's info
    Output:
    """
    client_from_name = chat_request_msg["client_from"]["name"]
    accepted_request = input(f"{client_from_name} sent you a chat request. Accept?[y/n]\n")

    client_from_port = chat_request_msg["client_from"]["p2p_port"]
    client_from_host = chat_request_msg["client_from"]["p2p_host"]

    if accepted_request == "y":
        # Connect to the client that sent the chat request
        p2p_client.connect((client_from_host, client_from_port))
        print(f"\nConnected to {client_from_name}!")
        print(f"\n===== Chat with {client_from_name} starts below ===== \n")


        # Send acceptance message to the client that sent the chat request
        # SEND IT THROUGH P2P CLIENT SOCKET
        acceptance_msg = json.dumps({"type": "chat_request_response", 
                                     "status": "accepted", 
                                     # use "client_from" here because chat request is 
                                     # "accepted" by the client_from
                                     "client_from": client_info_self["client_id"]})
        p2p_client.send(acceptance_msg.encode("utf-8"))

        chat_session(p2p_client)


    else:
        rejection_msg = json.dumps({"type": "chat_request_response", 
                                    "status": "rejected",
                                    "client_from": client_info_self["client_id"]})
        client.send(rejection_msg.encode("utf-8"))


def receive_cr_response(cr_response_msg):
    """
    Helper Function of receive() that processes chat request response.
    """
    if cr_response_msg["status"] == "accepted":
        print("Chat request accepted. You can start texting now!")
        in_p2p_server = True
        
    elif cr_response_msg["status"] == "rejected":
        pass


def receive_text(text_msg):
    """
    Helper Function of receive() that processes text. 

    input:

    Output:

    """
    text_msg = text_msg["msg"]
    print(text_msg)


def receive(server):
    """
    Function that helps receiving client chat requests.

    Input: server: socket, the server that is listening to incoming requests
    Output: None
    """
    while True:
        try:
            msg = json.loads(server.recv(1024).decode('utf-8'))

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


def send(p2p_socket: socket.socket):
    """
    Helper function to send messages.

    Input: p2p_socket: socket, the socket that is used to send messages
    Output: None
    """
    # Get and filter the message to send
    msg = input()
    msg = f"[{username}]: " + msg
    msg_json = json.dumps({"type": "chat", "msg": msg})
    msg_encoded = msg_json.encode('utf-8')
    # Send the message to the server
    p2p_socket.send(msg_encoded)




# While loop that keeps the client end running
threading.Thread(target=send_chat_request).start()
threading.Thread(target=receive, args=(client,)).start()


