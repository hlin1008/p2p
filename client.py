import socket
import threading
import json
import random

# Define basic HOST/PORT parameters
HOST = '0.0.0.0'
PORT = 65431

# Global flags
incoming_chat_request = None
IN_CHAT_SESSION = threading.Event()

# Initiates P2P Server Socket
p2p_server_host = '0.0.0.0'
p2p_server_port = random.randint(50001, 60000)
p2p_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
p2p_server.bind((HOST, p2p_server_port))
p2p_server.listen()

# Get Username, Initiate client Socket and establish Connection
username = input("Enter name: ")
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((HOST, PORT))
userinfo = {"name": username, "p2p_port": p2p_server_port, "p2p_host": p2p_server_host}
client.send(json.dumps(userinfo).encode('utf-8'))

# Receive initial client list
client_list_raw = json.loads(client.recv(1024).decode('utf-8'))
print("\nOnline Users:")
for user in client_list_raw["users"]:
    if user["name"] != username:
        print(f"- {user['name']}")

client_list = client_list_raw["users"]
client_info_self = client_list_raw["client_info"]

# Create p2p client socket for outgoing connections
p2p_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

def main_loop():
    global incoming_chat_request
    while True:
        if incoming_chat_request:
            handle_incoming_chat()

        cmd = input("\nType 'chat' to chat, or 'exit' to quit: ").strip()
        if cmd == "chat":
            send_chat_request()
        elif cmd == "exit":
            print("Exiting...")
            client.close()
            break
        else:
            print("Unknown command.")

def send_chat_request():
    global IN_CHAT_SESSION
    client_to_name = input("\nWho would you like to talk to?\n").strip()
    client_to = next((c for c in client_list if c["name"] == client_to_name), None)

    if client_to:
        chat_request = json.dumps({"type": "chat_request", "client_to": client_to, "client_from": client_info_self}).encode('utf-8')
        client.send(chat_request)
        p2p_conn, _ = p2p_server.accept()

        status_message = json.loads(p2p_conn.recv(1024).decode('utf-8'))
        if status_message["status"] == "accepted":
            IN_CHAT_SESSION.set()
            print(f"\nConnected to {client_to_name}!\n===== Chat with {client_to_name} starts below =====\n")
            chat_session(p2p_conn)
        else:
            print(f"\n{client_to_name} rejected your chat request.")
            p2p_conn.close()

def chat_session(p2p_socket):
    threading.Thread(target=receive_messages, args=(p2p_socket,), daemon=True).start()
    while IN_CHAT_SESSION.is_set():
        msg = input()
        full_msg = json.dumps({"type": "chat", "msg": f"[{username}]: {msg}"})
        p2p_socket.send(full_msg.encode('utf-8'))

def receive_messages(sock):
    while True:
        try:
            msg = sock.recv(1024)
            if not msg:
                break
            data = json.loads(msg.decode('utf-8'))
            print(f"\n{data['msg']}")
        except:
            break

def receive(server):
    global incoming_chat_request
    while True:
        try:
            msg = json.loads(server.recv(1024).decode('utf-8'))
            if msg["type"] == "chat_request":
                incoming_chat_request = msg
            elif msg["type"] == "chat":
                print(f"\n{msg['msg']}")
            elif msg["type"] == "server_broadcast":
                print(msg["msg"])
        except Exception as e:
            print(f"[ERROR] {e}")
            break

def handle_incoming_chat():
    global incoming_chat_request
    global IN_CHAT_SESSION

    client_from_name = incoming_chat_request["client_from"]["name"]
    client_from_port = incoming_chat_request["client_from"]["p2p_port"]
    client_from_host = incoming_chat_request["client_from"]["p2p_host"]

    accept = input(f"\n{client_from_name} sent you a chat request. Accept? (y/n): ").strip()

    temp_p2p_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    temp_p2p_client.connect((client_from_host, client_from_port))

    if accept.lower() == 'y':
        IN_CHAT_SESSION.set()
        acceptance_msg = {"type": "chat_request_response", "status": "accepted", "client_from": client_info_self}
        client.send(json.dumps(acceptance_msg).encode('utf-8'))
        temp_p2p_client.send(json.dumps(acceptance_msg).encode('utf-8'))

        print(f"\nConnected to {client_from_name}!\n===== Chat with {client_from_name} starts below =====\n")
        chat_session(temp_p2p_client)
    else:
        rejection_msg = {"type": "chat_request_response", "status": "rejected", "client_from": client_info_self}
        client.send(json.dumps(rejection_msg).encode('utf-8'))
        temp_p2p_client.send(json.dumps(rejection_msg).encode('utf-8'))
        temp_p2p_client.close()

    incoming_chat_request = None

# Start background receive thread
threading.Thread(target=receive, args=(client,), daemon=True).start()

# Start user input loop
main_loop()