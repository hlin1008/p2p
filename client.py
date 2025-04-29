import threading
import requests
import json
import random
import socket



SERVER_URL = "http://localhost:65431"  # URL of the server
client_info = None  # Client info to be sent to server, stored at client end
other_clients = []  # List of other clients. 
connections = {}  # Dictionary to store P2P connections. key: client_id, value: socket object
texts = {} # Dictionary to store texts. key: client_id, value: list of texts

# Change to ip later
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
    global client_info
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
    global client_info
    response = requests.get(f"{SERVER_URL}/users")
    if response.status_code == 200:
        users = response.json()
        for user in users:
            other_clients.append(user)
    

def send_chat_request():
    client_to_id = input("Enter the client ID you want to chat with: ")
    response = requests.post(f"{SERVER_URL}/send_chat_request", json={
        "client_from_id": client_info["client_id"],
        "client_to_id": client_to_id
    })

    if response.status_code == 200:
        print("Offer sent successfully.")
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
                    threading.Thread(target=accept_new_connection).start()
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
        print("5. Fetch Responses")
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
        client_connecting_info = other_clients[client_id]
        conn.connect((client_connecting_info["p2p_host"], client_connecting_info["p2p_port"]))
        connections[client_id] = conn
    except Exception as e:
        pass


def p2p_send_text(client_id, text):
    """
    Function to send text to another client using P2P.
    """
    if client_id not in connections:
        print(f"Not connected to {client_id['name']}.")
        return

    try:
        conn = connections[client_id]
        conn.sendall(text.encode())
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
    client_id = conn.recv(1024).decode()
    connections[client_id] = conn
        

"""def listen_for_connections():
    while True:
        try:
            conn, addr = p2p_server.accept()
            connections[addr] = conn
        except Exception as e:
            print(f"Error accepting connection: {e}")

def load_texts():
    for connection in connections.values():
            data = connection.recv(1024).decode()
            texts[connection] = json.loads(data)
        except Exception as e:
            print(f"Error loading texts: {e}")"""

    
# === Debug ===
def show_all_data():
    print("\n=== Client Info ===")
    print(json.dumps(client_info, indent=4))
    print("\n=== Other Clients ===")
    print(json.dumps(other_clients, indent=4))
    print("\n=== Connections ===")
    print(json.dumps(connections, indent=4))
    print("\n=== Texts ===")
    print(json.dumps(texts, indent=4))


# Start user menu
"""threading.Thread(target=listen_for_connections).start()
threading.Thread(target=load_all_texts).start()"""
threading.Thread(target=update_client_info).start()
main_menu()


