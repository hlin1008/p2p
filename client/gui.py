import tkinter as tk
from tkinter import ttk
from client_chat_handler import ClientChatHandler
import threading


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
        friends_and_online_clients = friends_and_online_clents_window(new_window, self.cch)
        
        # Start the main loop for the new window
        new_window.mainloop()



class friends_and_online_clents_window:
    def __init__(self, master:tk.Tk, cch:ClientChatHandler):
        self.master = master
        self.master.title("Friends and Online Clients")
        self.master.geometry("800x550")

        notebook = ttk.Notebook(self.master)
        notebook.pack(pady=10, expand=True)

        register_frame = tk.Frame(notebook, width=400, height=280)
        chat_frame = tk.Frame(notebook, width=400, height=280)
        register_frame.pack(fill="both", expand=True)
        chat_frame.pack(fill="both", expand=True)
        notebook.add(register_frame, text="Register")
        notebook.add(chat_frame, text="Chat")

        # Specify the ClientChatHandler instance
        self.cch = cch

        # Create frames
        self.create_widgets()

    def create_widgets(self):
        # Top frame
        top_frame = tk.Frame(self.master)
        top_frame.pack(expand=True, fill='both')
        title = tk.Label(top_frame, text="Friends and Online Clients", font=("Helvetica", 16))
        title.place(relx=0.5, rely=0.8, anchor='center')

        # Bottom frame
        bottom_frame = tk.Frame(self.master)
        bottom_frame.pack(expand=True, fill='both')



if __name__ == "__main__":
    root = tk.Tk()
    cch = ClientChatHandler()
    app = RegisterWindow(root, cch=cch)
    root.mainloop()


