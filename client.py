import threading
import requests
import json


SERVER_URL = "http://localhost:65431"  # URL of the server

client_info = None  # Client info to be sent to server, stored at client end

def register_client():
    """
    Function to register the client with the server.
    """
    global client_info
    username = input("Enter your name: ")
    p2p_host = input("Enter your P2P host: ")
    p2p_port = int(input("Enter your P2P port: "))

    client_info = {
        "name": username,
        "p2p_host": p2p_host,
        "p2p_port": p2p_port
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

def check_chat_request():
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

def check_cr_response():
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
                    print("You can now start direct P2P connection.")
        else:
            print("No new responses.")
    else:
        print("Failed to fetch responses.")

def main_menu():
    while True:
        print("\n===== Menu =====")
        print("1. Register")
        print("2. View Online Users")
        print("3. Send Chat Offer")
        print("4. Fetch Offers / Responses Manually")
        print("0. Exit")
        choice = input("Enter your choice: ").strip()

        if choice == "1":
            register_client()
        elif choice == "2":
            view_users()
        elif choice == "3":
            send_chat_request()
        elif choice == "4":
            check_chat_request()
            check_cr_response()
        elif choice == "0":
            print("Goodbye!")
            break
        else:
            print("Invalid choice!")



# Start user menu
main_menu()