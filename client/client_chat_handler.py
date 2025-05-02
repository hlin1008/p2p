import threading
import requests
import json
import random
import socket
import time
from datetime import datetime

class ClientChatHandler:
    def __init__(self, server_url="http://localhost:65431"):
        self.server_url = server_url
        self.client_info = None
        self.other_clients = {}
        self.connections = {}
        self.texts = {}
        self.chat_requests = {}
        self.registered = False

        # Setup P2P Server
        self.p2p_server_host = '0.0.0.0'
        self.p2p_server_port = random.randint(50001, 60000)
        self.p2p_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.p2p_server.bind((self.p2p_server_host, self.p2p_server_port))
        self.p2p_server.listen()

    def register(self, username):
        self.client_info = {
            "name": username,
            "p2p_host": self.p2p_server_host,
            "p2p_port": self.p2p_server_port
        }

        response = requests.post(f"{self.server_url}/register", json=self.client_info)
        if response.status_code == 200:
            self.client_info["client_id"] = response.json()["your_info"]["client_id"]
            self.registered = True
            return True
        return False


    def view_users(self):
        response = requests.get(f"{self.server_url}/users")
        if response.status_code == 200:
            users = response.json()
            print("\n=== Online Users ===")
            for user in users:
                if user["client_id"] != self.client_info["client_id"]:
                    print(f"- {user['name']} ({user['client_id']})")
        else:
            print("Failed to fetch users.")

    def automatic_update_client_info(self):
        """
        Function to update the client info with the server.
        """
        while self.registered:
            response = requests.get(f"{self.server_url}/users")
            if response.status_code == 200:
                users = response.json()
                for user in users:
                    user_id = user["client_id"]
                    if user_id not in self.other_clients and user_id != self.client_info["client_id"]:
                        # Add the user to other_clients
                        self.other_clients[user_id] = user
                time.sleep(10)
            else:
                print("Failed to fetch users.")

    def start_client_info_update(self):
        threading.Thread(target=self.automatic_update_client_info).start()


    def send_chat_request(self, client_id):
        response = requests.post(f"{self.server_url}/send_chat_request", json={
            "client_from_id": self.client_info["client_id"],
            "client_to_id": client_id
        })

        if response.status_code == 200:
            print("Offer sent successfully.")
            threading.Thread(target=self.fetch_cr_response, daemon=True).start()  # automate fetching responses
        else:
            print("Failed to send offer.")

    def fetch_chat_request(self):
        response = requests.get(f"{self.server_url}/check_chat_request/{self.client_info['client_id']}")
        if response.status_code == 200:
            offers = response.json()
            if offers:
                for offer in offers:
                    offer["name"] = self.other_clients[offer["from_client_id"]]["name"]
                    self.chat_requests[offer["from_client_id"]] = offer
            else:
                print("No new offers.")
        else:
            print("Failed to fetch offers.")

    def send_cr_response(self,from_id, status):
        response = requests.post(f"{self.server_url}/send_offer_response", json={
            "client_from_id": self.client_info["client_id"],
            "client_to_id": from_id,
            "status": status
        })

        if response.status_code == 200:
            print("Offer response sent successfully.")
        else:
            print("Failed to send offer response.")

    def fetch_cr_response(self):
        response = requests.get(f"{self.server_url}/fetch_responses/{self.client_info['client_id']}")
        if response.status_code == 200:
            responses = response.json()
            if responses:
                for res in responses:
                    from_id = res["from_client_id"]
                    status = res["status"]
                    print(f"\nOffer to {from_id} was {status}!")
                    if status == "accepted":
                        # TODO: Start P2P connection here
                        self.p2p_connect(from_id)
                        print("You can now start direct P2P connection.")
            else:
                print("No new responses.")
        else:
            print("Failed to fetch responses.")


    # === P2P Connection ===    
    def p2p_connect(self,client_id):
        """
        Function to connect to another client using P2P.
        """
        if client_id in self.connections:
            print(f"Already connected to {client_id}.")
            return

        try:
            conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_connecting_info = self.other_clients[client_id] # retrieve client info from other_clients
            conn.connect((client_connecting_info["p2p_host"], client_connecting_info["p2p_port"]))
            self.connections[client_id] = conn

            # First thing to do is send the client_id
            msg_data = {
                "type": "p2p_connection_info",
                "info": {
                    "client_id": self.client_info["client_id"]
                }
            }
            msg_data = json.dumps(msg_data)
            conn.send(msg_data.encode())
            
        except Exception as e:
            print("Error")

    def p2p_send_text(self,client_id, text):
        """
        Function to send text to another client using P2P.
        """
        if client_id not in self.connections:
            print(f"Not connected to {client_id}.")
            return

        try:
            # Get the current date and time
            dt = datetime.now()
            dt_formatted = dt.strftime("%Y-%m-%d %H:%M:%S")
            self_id = self.client_info["client_id"]
            msg = {"text": text, "datetime": dt_formatted, "from": self_id}
            msg_data = {
                "type": "text",
                "info": msg
            }
            msg_data = json.dumps(msg_data)
            # Send the text to the client
            conn = self.connections[client_id]
            conn.send(msg_data.encode())
            if client_id not in texts:
                self.texts[client_id] = []
            self.texts[client_id].append(msg)
        except Exception as e:
            print(f"Failed to send text: {e}")

    def accept_new_connection(self):
        """
        Function to accept new P2P connections.
        Have socket wait for incoming connections.
        First message received is the client_id. Use it to identify the client.
        Store the connection in the connections dictionary.
        """
        conn, addr = self.p2p_server.accept()
        self.load_sort_texts_connection(conn)
        
    def load_sort_texts_connection(self,conn):
        """
        Function to load and sort texts from all connections.
        Load texts from each connection and sort them by timestamp.
        Loads every 10 seconds.
        """
        msg_data = conn.recv(1024).decode()
        msg_data = json.loads(msg_data)
        if msg_data:

            # If message is text
            if msg_data["type"] == "text":
                msg = msg_data["info"]
                message_from_id = msg["from"]
                if message_from_id not in texts:
                    self.texts[message_from_id] = []
                
                chat_history = self.texts[message_from_id]
                chat_history.append(msg)
            
            # If message is an accepted connection
            elif msg_data["type"] == "p2p_connection_info":
                # Add the client to the connections dictionary
                client_id = msg_data["info"]["client_id"]
                if client_id not in self.connections:
                    self.connections[client_id] = conn       
            
        time.sleep(10)

    def automatic_load_and_sort_texts(self):
        """
        Function to loop "load_sort_texts_connection" every 10 seconds.
        This is to keep the chat history updated.
        Ran in a separate thread.
        """
        while True:
            for connection in self.connections.values():
                # Get client id from connection
                self.load_sort_texts_connection(connection)

    
    # === Debug ===
    def show_all_data(self):
        print("\n=== Client Info ===")
        print(self.client_info)
        print("\n=== Other Clients ===")
        print(self.other_clients)
        print("\n=== Connections ===")
        print(self.connections)
        print("\n=== Texts ===")
        print(self.texts)


    """threading.Thread(target=automatic_load_and_sort_texts, daemon=True).start()"""



