from tkinter import *
import threading
import requests
import client.client as client  # your client-side socket/chat logic

SERVER_URL = "http://localhost:8000"  # adjust if needed

client_id = None

def register():
    global client_id
    name = name_entry.get()
    if not name:
        log("Enter a name first")
        return

    payload = {
        "name": name,
        "p2p_host": "localhost",
        "p2p_port": 6000  # or generate dynamically
    }

    try:
        res = requests.post(f"{SERVER_URL}/register", json=payload)
        if res.status_code == 200:
            data = res.json()
            client_id = data["your_info"]["client_id"]
            log(f"Registered as {name}")
            update_users()
        else:
            log("Registration failed")
    except Exception as e:
        log(f"Error: {e}")


def update_users():
    try:
        res = requests.get(f"{SERVER_URL}/users")
        users = res.json()
        user_list.delete(0, END)
        for u in users:
            if u["client_id"] != client_id:
                user_list.insert(END, f"{u['name']} ({u['client_id']})")
    except:
        log("Failed to fetch users")


def send_chat_request():
    selection = user_list.curselection()
    if not selection:
        log("Select a user to chat with")
        return
    target_line = user_list.get(selection[0])
    target_id = target_line.split("(")[-1].strip(")")

    payload = {
        "client_from_id": client_id,
        "client_to_id": target_id
    }

    try:
        res = requests.post(f"{SERVER_URL}/send_chat_request", json=payload)
        if res.status_code == 200:
            log("Chat request sent")
        else:
            log("Failed to send request")
    except:
        log("Error sending request")


def poll_responses():
    while True:
        if client_id:
            try:
                res = requests.get(f"{SERVER_URL}/fetch_responses/{client_id}")
                responses = res.json()
                for r in responses:
                    status = r.get("status")
                    sender = r.get("from_client_id")
                    if status == "accepted":
                        log(f"Chat accepted by {sender}")
                        threading.Thread(target=client.connect_to_peer, args=(sender,), daemon=True).start()
            except:
                pass
        time.sleep(3)


def log(msg):
    chat_display.insert(END, msg + "\n")
    chat_display.see(END)


# === GUI START ===
root = Tk()
root.title("P2P Chat GUI")

Label(root, text="Your Name:").grid(row=0, column=0)
name_entry = Entry(root)
name_entry.grid(row=0, column=1)
Button(root, text="Register", command=register).grid(row=0, column=2)

Label(root, text="Online Users:").grid(row=1, column=0, sticky=W)
user_list = Listbox(root, width=50)
user_list.grid(row=2, column=0, columnspan=2)
Button(root, text="Send Chat Request", command=send_chat_request).grid(row=2, column=2)

chat_display = Text(root, height=15, width=70)
chat_display.grid(row=3, column=0, columnspan=3)

# === Poll Responses in Background ===
threading.Thread(target=poll_responses, daemon=True).start()

root.mainloop()
