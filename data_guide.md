### Data Guide
1. User List
    
    {"type": "user_list",

    "users": [
    {
      "name": "Alice",
      "client_id": "uuid1",
      "client_port": 65435
    },
    ...
  ],
 
    
    "client_info": {
    "name": "client's name",
    "id": "uuid2",
    "client_port": 65432
  }
}

    **Note:** Information in *client_info* is current client's own info. Anything that's in *users* is info of all other clients.



2. chat_request

    {
    "type": "chat_request",


    "client_to": {
    "name": "Bob",
    "client_id": "uuid3",
    "client_port": 65436
  },


    "client_port": 51000  // port on which the sender's P2P server is listening
}


3. chat_request_response


    {
    "type": "chat_request_response",

    "status": "accepted",  // or "rejected"

    "client_id": "uuid3"   // ID of the client sending the response
}
