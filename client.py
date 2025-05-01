import threading
import requests
import json
import random
import socket
import time
from datetime import datetime

# === Global Variables ===
SERVER_URL = "http://localhost:65431"  # URL of the server
client_info = None  # Client info to be sent to server, stored at client end
other_clients = {}  # List of other clients. 
connections = {}  # Dictionary to store P2P connections. key: client_id, value: socket object
texts = {} # Dictionary to store texts. key: client_id, value: list of texts
registered = False

# === P2P Server Setup ===
p2p_server_host = '0.0.0.0'
p2p_server_port = random.randint(50001,60000) 
p2p_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
p2p_server.bind((p2p_server_host, p2p_server_port))
p2p_server.listen()

# === Requests to Server ===
def register_client():
    """
    Function to register the client with the server.
    """
    global client_info, registered
    username = input("Enter your name: ")
    # p2p_host = input("Enter your P2P host: ")
    # p2p_port = int(input("Enter your P2P port: "))

    client_info = {
        "name": username,
        "p2p_host": p2p_server_host,
        "p2p_port": p2p_server_port
    }

    response = requests.post(f"{SERVER_URL}/register", json=client_info)
    if response.status_code == 200:
        # Add server-generated client_id to client_info
        client_info["client_id"] = response.json()["your_info"]["client_id"]

        print("Client registered successfully.")
        registered = True
        threading.Thread(target=update_client_info, daemon=True).start()  # start updating client info
        return response.json()
    
    else:
        print("Failed to register client.")
        return None
    # could later change so that return client info from response body

def view_users():
    response = requests.get(f"{SERVER_URL}/users")
    if response.status_code == 200:
        users = response.json()
        print("\n=== Online Users ===")
        for user in users:
            if user["client_id"] != client_info["client_id"]:
                print(f"- {user['name']} ({user['client_id']})")
    else:
        print("Failed to fetch users.")

def update_client_info():
    """
    Function to update the client info with the server.
    """
    global other_clients
    while registered:
        response = requests.get(f"{SERVER_URL}/users")
        if response.status_code == 200:
            users = response.json()
            for user in users:
                user_id = user["client_id"]
                if user_id not in other_clients and user_id != client_info["client_id"]:
                    # Add the user to other_clients
                    other_clients[user_id] = user
            time.sleep(15)
        else:
            print("Failed to fetch users.")
    
def send_chat_request():
    client_to_id = input("Enter the client ID you want to chat with: ")
    response = requests.post(f"{SERVER_URL}/send_chat_request", json={
        "client_from_id": client_info["client_id"],
        "client_to_id": client_to_id
    })

    if response.status_code == 200:
        print("Offer sent successfully.")
        threading.Thread(target=fetch_cr_response, daemon=True).start()  # automate fetching responses
    else:
        print("Failed to send offer.")

def fetch_chat_request():
    response = requests.get(f"{SERVER_URL}/check_chat_request/{client_info['client_id']}")
    if response.status_code == 200:
        offers = response.json()
        if offers:
            for offer in offers:
                from_id = offer["from_client_id"]
                print(f"\nReceived chat offer from {from_id}")
                decision = input("Accept (a) or Reject (r)? ").strip().lower()
                status = "accepted" if decision == "a" else "rejected"
                send_cr_response(from_id, status)

                if decision == "a":
                    threading.Thread(target=accept_new_connection, daemon=True).start()
        else:
            print("No new offers.")
    else:
        print("Failed to fetch offers.")

def send_cr_response(from_id, status):
    response = requests.post(f"{SERVER_URL}/send_offer_response", json={
        "client_from_id": client_info["client_id"],
        "client_to_id": from_id,
        "status": status
    })

    if response.status_code == 200:
        print("Offer response sent successfully.")
    else:
        print("Failed to send offer response.")

def fetch_cr_response():
    response = requests.get(f"{SERVER_URL}/fetch_responses/{client_info['client_id']}")
    if response.status_code == 200:
        responses = response.json()
        if responses:
            for res in responses:
                from_id = res["from_client_id"]
                status = res["status"]
                print(f"\nOffer to {from_id} was {status}!")
                if status == "accepted":
                    # TODO: Start P2P connection here
                    p2p_connect(from_id)
                    print("You can now start direct P2P connection.")
        else:
            print("No new responses.")
    else:
        print("Failed to fetch responses.")

# === Main Menu ===
def main_menu():
    while True:
        print("\n===== Menu =====")
        print("1. Register")
        print("2. View Online Users")
        print("3. Send Chat Offer")
        print("4. Fetch Offers")
        print("5. Fetch Responses(Manual)")
        print("6. Send Text")
        print("0. Exit")
        choice = input("Enter your choice: ").strip()

        if choice == "1":
            register_client()
        elif choice == "2":
            view_users()
        elif choice == "3":
            send_chat_request()
        elif choice == "4":
            fetch_chat_request()
        elif choice == "5":
            fetch_cr_response()
        elif choice == "6":
            client_id = input("Enter the client ID you want to send text to: ")
            text = input("Enter the text: ")
            p2p_send_text(client_id, text)
        elif choice == "7":
            show_all_data()
        elif choice == "0":
            print("Goodbye!")
            break
        else:
            print("Invalid choice!")

# === P2P Connection ===    
def p2p_connect(client_id):
    """
    Function to connect to another client using P2P.
    """
    global connections
    if client_id in connections:
        print(f"Already connected to {client_id}.")
        return

    try:
        conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_connecting_info = other_clients[client_id] # retrieve client info from other_clients
        conn.connect((client_connecting_info["p2p_host"], client_connecting_info["p2p_port"]))
        connections[client_id] = conn

        # First thing to do is send the client_id
        msg_data = {
            "type": "p2p_connection_info",
            "info": {
                "client_id": client_info["client_id"]
            }
        }
        msg_data = json.dumps(msg_data)
        conn.send(msg_data.encode())
        
    except Exception as e:
        print("Error")

def p2p_send_text(client_id, text):
    """
    Function to send text to another client using P2P.
    """
    global texts
    if client_id not in connections:
        print(f"Not connected to {client_id}.")
        return

    try:
        # Get the current date and time
        dt = datetime.now()
        dt_formatted = dt.strftime("%Y-%m-%d %H:%M:%S")
        self_id = client_info["client_id"]
        msg = {"text": text, "datetime": dt_formatted, "from": self_id}
        msg_data = {
            "type": "text",
            "info": msg
        }
        msg_data = json.dumps(msg_data)
        # Send the text to the client
        conn = connections[client_id]
        conn.send(msg_data.encode())
        if client_id not in texts:
            texts[client_id] = []
        texts[client_id].append(msg)
    except Exception as e:
        print(f"Failed to send text: {e}")

def accept_new_connection():
    """
    Function to accept new P2P connections.
    Have socket wait for incoming connections.
    First message received is the client_id. Use it to identify the client.
    Store the connection in the connections dictionary.
    """
    global connections
    conn, addr = p2p_server.accept()
    load_sort_texts_connection(conn)
    

def load_sort_texts_connection(conn):
    """
    Function to load and sort texts from all connections.
    Load texts from each connection and sort them by timestamp.
    Loads every 10 seconds.
    """
    global connections
    msg_data = conn.recv(1024).decode()
    msg_data = json.loads(msg_data)
    if msg_data:

        # If message is text
        if msg_data["type"] == "text":
            msg = msg_data["info"]
            message_from_id = msg["from"]
            if message_from_id not in texts:
                texts[message_from_id] = []
            
            chat_history = texts[message_from_id]
            chat_history.append(msg)
        
        # If message is an accepted connection
        elif msg_data["type"] == "p2p_connection_info":
            # Add the client to the connections dictionary
            client_id = msg_data["info"]["client_id"]
            if client_id not in connections:
                connections[client_id] = conn       
        
    time.sleep(10)

def automatic_load_and_sort_texts():
    """
    Function to loop "load_sort_texts_connection" every 10 seconds.
    This is to keep the chat history updated.
    Ran in a separate thread.
    """
    global texts, connections
    while True:
        for connection in connections.values():
            # Get client id from connection
            load_sort_texts_connection(connection)

   
# === Debug ===
def show_all_data():
    print("\n=== Client Info ===")
    print(client_info)
    print("\n=== Other Clients ===")
    print(other_clients)
    print("\n=== Connections ===")
    print(connections)
    print("\n=== Texts ===")
    print(texts)


# Start user menu
if __name__ == "__main__":
    threading.Thread(target=automatic_load_and_sort_texts, daemon=True).start()
    main_menu()


