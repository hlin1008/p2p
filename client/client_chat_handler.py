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

        # for updating GUI
        self.gui_callback_map = {}

    def register(self, username):
        self.client_info = {
            "name": username,
            "p2p_host": self.p2p_server_host,
            "p2p_port": self.p2p_server_port
        }

        response = requests.post(f"{self.server_url}/register", json=self.client_info)
        if response.status_code == 200:
            self.client_info["client_id"] = response.json()["your_info"]["client_id"]
            threading.Thread(target=self.listen_for_incoming_connections, daemon=True).start()
            self.registered = True
            return True
        return False

    def fetch_user_list(self):
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
                        user["relation"] = "general"
                        self.other_clients[user_id] = user
                time.sleep(10)
            else:
                print("Failed to fetch users.")

    def start_client_info_autoupdate(self):
        threading.Thread(target=self.fetch_user_list).start()

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

        if status == "accept":
            self.other_clients[from_id]["relation"] = "friend"
            

        if response.status_code == 200:
            print("Offer response sent successfully.")
        else:
            print("Failed to send offer response.")

    def fetch_cr_response(self):
        while True:
            response = requests.get(f"{self.server_url}/fetch_responses/{self.client_info['client_id']}")
            if response.status_code == 200:
                responses = response.json()
                if responses:
                    for res in responses:
                        from_id = res["from_client_id"]
                        status = res["status"]
                        if status == "accept":
                            self.other_clients[from_id]["relation"] = "friend"
                            self.p2p_connect(from_id)
                            print("You can now start direct P2P connection.")
                else:
                    print("No new responses.")
            else:
                print("Failed to fetch responses.")
            time.sleep(10)


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

            # Start a new thread to listen for incoming messages from this connection
            threading.Thread(target=self.handle_client_connection, args=(conn,), daemon=True).start()


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
            if client_id not in self.texts:
                self.texts[client_id] = []
            self.texts[client_id].append(msg)
        except Exception as e:
            print(f"Failed to send text: {e}")

    def listen_for_incoming_connections(self):
        while True:
            conn, _ = self.p2p_server.accept()
            threading.Thread(target=self.handle_client_connection, args=(conn,), daemon=True).start()

    def handle_client_connection(self, conn):
        while True:
            try:
                data = conn.recv(1024)
                if not data:
                    break
                msg_data = json.loads(data.decode())
                self.handle_message(conn, msg_data)
            except Exception as e:
                print(f"Error handling incoming message: {e}")
                break

    def handle_message(self, conn, msg_data):
        if msg_data["type"] == "text":
            msg = msg_data["info"]
            from_id = msg["from"]
            # Save message
            if from_id not in self.texts:
                self.texts[from_id] = []
            self.texts[from_id].append(msg)

            # UPDATE GUI
            if from_id in self.gui_callback_map:
                self.gui_callback_map[from_id](msg)

        elif msg_data["type"] == "p2p_connection_info":
            self.connections[msg_data["info"]["client_id"]] = conn

              
    


    
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



