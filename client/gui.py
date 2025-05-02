import tkinter as tk
from tkinter import ttk
from client_chat_handler import ClientChatHandler
import threading

import time

# global variable 
other_clients = {}



# Create the original registering window
class RegisterWindow:
    def __init__(self, master:tk.Tk, cch:ClientChatHandler):
        self.master = master
        self.master.title("Register/Login")
        self.master.geometry("400x600")

        # Specify the ClientChatHandler instance
        self.cch = cch

        # Create frames
        self.create_widgets()

    def create_widgets(self):
        # Top frame
        top_frame = tk.Frame(self.master)
        top_frame.pack(expand=True, fill='both')
        title = tk.Label(top_frame, text="Register/Login", font=("Helvetica", 16))
        title.place(relx=0.5, rely=0.8, anchor='center')

        # Bottom frame
        bottom_frame = tk.Frame(self.master)
        bottom_frame.pack(expand=True, fill='both')

        container = tk.Frame(bottom_frame)
        container.place(relx=0.5, rely=0.1, anchor='center')

        tk.Label(container, text="Username:").grid(row=0, column=0, padx=5, pady=5)
        name_entry = tk.Entry(container)
        name_entry.grid(row=0, column=1, padx=5, pady=5)
        self.name_entry = name_entry


        button_container = tk.Frame(bottom_frame)
        button_container.place(relx=0.5, rely=0.4, anchor='center')  
        tk.Button(button_container, text="Register", command=self.register).grid(row=0,column=0, padx=5, pady=5)

    def register(self):
        """
        Pack all functions that register button should call into one. 
        """
        username = self.name_entry.get()
        chat_handler = self.cch 
        chat_handler.register(username)

        # Close the register window
        self.master.destroy()
        # Open the friends and online clients window
        self.open_friends_and_online_clients_window()

    def open_friends_and_online_clients_window(self):
        """
        Open the friends and online clients window.
        """
        # Create a new window
        new_window = tk.Tk()
        new_window.title("Friends and Online Clients")
        new_window.geometry("800x550")

        # Create an instance of the friends_and_online_clents_window class
        friends_and_online_clients = ClientFinderWindow(new_window, self.cch)
        
        # Start the main loop for the new window
        new_window.mainloop()


class ClientFinderWindow:
    def __init__(self, master:tk.Tk, cch:ClientChatHandler):
        self.master = master
        self.master.title("Friends and Online Clients")
        self.master.geometry("800x550")

        notebook = ttk.Notebook(self.master)
        notebook.pack(pady=10, expand=True)
        self.notebook = notebook

        self.cch = cch

        self.user_id_map = [] # List to store user IDs
        self.chat_request_map = [] # List to store chat request IDs

        self.create_friends_frame()
        self.create_online_users_frame()
        self.create_chat_request_frame()

        
        

    def create_friends_frame(self):
        # Create a frame for friends
        friends_frame = tk.Frame(self.notebook, width=800, height=550)
        friends_frame.pack(fill="both", expand=True)
        self.notebook.add(friends_frame, text="Friends")

    def create_online_users_frame(self):
        # Create a frame for online users
        online_users_frame = tk.Frame(self.notebook, width=800, height=550)
        online_users_frame.pack(fill="both", expand=True)
        self.notebook.add(online_users_frame, text="Online Users")

        # Create a listbox to display online users
        online_users_listbox = tk.Listbox(online_users_frame, width=50, height=20,
                                          font=("Helvetica", 16))
        online_users_listbox.pack(pady=10)
        self.online_users_listbox = online_users_listbox

        # Autoupdate the online users list
        self.cch.start_client_info_update()
        time.sleep(0.5)

        user_list = self.cch.other_clients
        for user_id, user_info in user_list.items():
            self.online_users_listbox.insert(tk.END, f"{user_info['name']}")
            self.user_id_map.append(user_id)
        
        # Create a scrollbar for the listbox
        scrollbar = tk.Scrollbar(online_users_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        online_users_listbox.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=online_users_listbox.yview)

        # Create a button frame to gather buttons
        button_frame = tk.Frame(online_users_frame)
        button_frame.pack(pady=10)

        # Create a button to refresh the online users list
        refresh_button = tk.Button(button_frame, text="Refresh", 
                                    command=self.refresh_online_users)
        refresh_button.grid(row=0, column=0, padx=5, pady=5)

        # Create a button to send chat request
        send_request_button = tk.Button(button_frame, text="Send Chat Request", 
                                        command=lambda:self.send_chat_request())
        send_request_button.grid(row=0, column=1, padx=5, pady=5)
             
    def send_chat_request(self):
        """
        Send a chat request to the selected user.
        """
        selection = self.online_users_listbox.curselection()
        if selection:
            index = selection[0]
            user_id = self.user_id_map[index]
            self.cch.send_chat_request(user_id)
      
    def refresh_online_users(self):
        """
        Refresh the online users list.
        """
        self.online_users_listbox.delete(0, tk.END)
        self.user_id_map.clear()

        # Fetch the updated list of online users
        self.cch.start_client_info_update()
        time.sleep(0.5)
        user_list = self.cch.other_clients
        for user_id, user_info in user_list.items():
            self.online_users_listbox.insert(tk.END, f"{user_info['name']}")
            self.user_id_map.append(user_id)
        
    def create_chat_request_frame(self):
        online_users_frame = tk.Frame(self.notebook, width=800, height=550)
        online_users_frame.pack(fill="both", expand=True)
        self.notebook.add(online_users_frame, text="Chat Requests")

        # Create a listbox to display chat requests
        chat_requests_listbox = tk.Listbox(online_users_frame, width=50, height=20,
                                          font=("Helvetica", 16))
        chat_requests_listbox.pack(pady=10)
        self.chat_requests_listbox = chat_requests_listbox

        # Autoupdate the online users list
        self.cch.fetch_chat_request()
        time.sleep(0.5)

        chat_request_list = self.cch.chat_requests
        for user_id, user_info in chat_request_list.items():
            username = user_info["name"]
            self.chat_requests_listbox.insert(tk.END, f"{username}")
            self.chat_request_map.append(user_id)
        
        # Create a scrollbar for the listbox
        scrollbar = tk.Scrollbar(online_users_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        chat_requests_listbox.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=chat_requests_listbox.yview)

        # Create a button frame to gather buttons
        button_frame = tk.Frame(online_users_frame)
        button_frame.pack(pady=10)

        # Create a button to refresh the online users list
        refresh_button = tk.Button(button_frame, text="Refresh", 
                                    command=self.refresh_chat_requests)
        refresh_button.grid(row=0, column=0, padx=5, pady=5)

        # Create a button to send chat request
        accept_button = tk.Button(button_frame, text="Accept", 
                                        command=lambda:self.send_cr_response("accept"))
        accept_button.grid(row=0, column=1, padx=5, pady=5)
        reject_button = tk.Button(button_frame, text="Reject", 
                                        command=lambda:self.send_cr_response("reject"))
        reject_button.grid(row=0, column=2, padx=5, pady=5)
    
    def refresh_chat_requests(self):
        """
        Refresh the current chat requests.
        """
        self.chat_requests_listbox.delete(0, tk.END)
        self.chat_request_map.clear()

        # Fetch the updated list of online users
        self.cch.fetch_chat_request()
        time.sleep(0.5)
        chat_request_list = self.cch.chat_requests
        for user_id, user_info in chat_request_list.items():
            username = user_info["name"]
            self.chat_requests_listbox.insert(tk.END, f"{username}")
            self.chat_request_map.append(user_id)

    def send_cr_response(self, status:str):
        """
        Send a chat request to the selected user.
        """
        selection = self.chat_requests_listbox.curselection()
        if selection:
            index = selection[0]
            user_id = self.chat_request_map[index]
            self.cch.send_cr_response(user_id, status)
            
            # Remove the chat request from the list
            self.chat_requests_listbox.delete(index)
            self.chat_request_map.pop(index)
            print(f"Chat request from {user_id} has been {status}ed.")
        
        


    





if __name__ == "__main__":
    root = tk.Tk()
    cch = ClientChatHandler()
    app = RegisterWindow(root, cch=cch)
    root.mainloop()


