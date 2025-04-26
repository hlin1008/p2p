import socket
import threading
import json
import uuid

# Importing FastAPI and Pydantic for future use
from fastapi import FastAPI
from pydantic import BaseModel

# Define basic HOST/PORT parameters
HOST = '0.0.0.0'
PORT = 65431

CLIENTS = [] # List of connected clients
REQS = {} # For now, saving chat requests in a dict. Switching to SQLite later.
RESPONSES = {} # For now, saving chat request responses in a dict. Switching to SQLite later.

# initiate FastAPI
app = FastAPI()

# == Data Model for FastAPI ==
class NewUser(BaseModel):
    name: str
    p2p_host: str
    p2p_port: int

class ChatRequest(BaseModel):
    client_from_id: str 
    client_to_id: str

class ChatRequestResponse(BaseModel):
    client_from_id: str
    client_to_id: str
    status: str

# == Helper Functions ==
def filter_client_info(client_info:dict):
    """
    Helper function that extracts data from server end client info data that could be sent to client end.

    Input:
        client_info: dictionary, contains all server end data
    Output:
        filtered_client_info: dictionary, contains sendable client end data
    """
    return {"name": client_info["name"],
            "client_id": client_info["client_id"],
            "p2p_host": client_info["p2p_host"],
            "p2p_port": client_info["p2p_port"]}


def get_available_clients(client_id:str):
    """
    Function that takes in id of a client, returns a list of available clients(without self).

    Input: 
        client_id: string, the id of the client that is requesting available clients
    Output: 
        available_clients: list, a list of dictionary of available client's info
    """
    available_clients = []
    for client in CLIENTS:
        if client["client_id"] != client_id:
            filtered_info = filter_client_info(client)
            available_clients.append(filtered_info)
    return available_clients


# == FastAPI ==
@app.post("/register")
def handle_new_client(client: NewUser):
    """
    Helper function that handles a newly connected client. 
    Appends new user data, sends available client list to user, initiates listening.

    Inputs:
        conn: socket, connection of new client's socket
        addr: address of the client
    Outputs:
        N/A
    """
    # Receiving New User Data
    new_client_id = str(uuid.uuid4())
    new_client_info = { "client_id": new_client_id,
                        "name": client.name,
                        "p2p_host": client.p2p_host,
                        "p2p_port": client.p2p_port}
    
    CLIENTS.append(new_client_info)

    available_clients = [filter_client_info(c) for c in CLIENTS if c["client_id"] != new_client_id]

    return {
        "your_info": filter_client_info(new_client_info),
        "available_clients": available_clients
    }


@app.get("/users")
def get_users():
    return [filter_client_info(c) for c in CLIENTS]


@app.get("/user/{client_id}")
def get_user_info(client_id: str):
    for client in CLIENTS:
        if client["client_id"] == client_id:
            return filter_client_info(client)
    return {"error": "User not found"}

@app.post("/send_offer")
def send_offer(offer: ChatRequest):
    if offer.client_to_id not in REQS:
        REQS[offer.client_to_id] = []
    REQS[offer.client_to_id].append({
        "from_client_id": offer.client_from_id
    })
    return {"status": "Offer sent"}

@app.get("/fetch_offers/{client_id}")
def fetch_offers(client_id: str):
    return REQS.pop(client_id, [])

@app.post("/send_offer_response")
def send_offer_response(response: ChatRequestResponse):
    if response.client_to_id not in RESPONSES:
        RESPONSES[response.client_to_id] = []
    RESPONSES[response.client_to_id].append({
        "from_client_id": response.client_from_id,
        "status": response.status
    })
    return {"status": "Response sent"}

@app.get("/fetch_responses/{client_id}")
def fetch_responses(client_id: str):
    return RESPONSES.pop(client_id, [])

    
 