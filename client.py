import socket
import threading

# Define basic HOST/PORT parameters
HOST = '0.0.0.0'
PORT = 65433

# Get Username, Initiate client Socket and establish Connection
username = input("Enter your username: ")
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((HOST, PORT))

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