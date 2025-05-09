
# 📨 Peer-to-Peer Chat System

A Python-based peer-to-peer (P2P) chat system with centralized registration and local GUI-based messaging. The system allows clients to register with a central server, connect to other clients directly, and maintain persistent message logs using SQLite.

---

## 🚀 Features

- Peer-to-peer messaging with direct socket connections
- Central server for client discovery and registration
- Local SQLite database for message history
- Tkinter-based GUI for sending and receiving messages
- Modular code with separate handlers for client, database, and UI

---

## 🛠️ Project Structure

```
p2p-main/
│
├── server/
│   └── server.py              # Handles client registration and user list management
│
├── client/
│   ├── client_chat_handler.py # Client-side P2P communication logic
│   ├── database_handler.py    # Handles SQLite database storage of chat history
│   └── gui.py                 # Tkinter GUI frontend
```

---

## 📦 Requirements

- Python 3.8+
- No external libraries required (uses built-in `socket`, `sqlite3`, `tkinter`, `threading`)

---

## 🧪 How to Run

### 1. Start the Server
In a terminal:
```bash
cd server
python server.py
```

### 2. Launch Clients
Open two more terminals for separate clients:
```bash
cd client
python gui.py
```
You will be prompted for a username. Then, you'll be shown a list of online users to chat with.

---

## 💬 Example Output

Client A (Alice):
```
Enter username: Alice
Online users:
- Bob

You: Hello Bob!
```

Client B (Bob):
```
Enter username: Bob
Online users:
- Alice

Alice: Hello Bob!
You: Hey Alice, how are you?
```

Chats are logged locally in a SQLite database, ensuring persistence even if the application is closed.

---

## 🧠 Commentary on Implementation

- **Concurrency**: Multithreading ensures clients can listen and send messages simultaneously without freezing the GUI.
- **Extensibility**: Clear separation of concerns allows for easy expansion (e.g., encryption, media messages).
- **GUI**: The tkinter interface is minimal but functional, with auto-scroll and message entry features.
- **Storage**: SQLite is a great choice for lightweight local persistence and supports chat history features.

---

## 🔬 Testing

> ⚠️ **No unit tests were provided**, but adding them is recommended. Suggested test cases:
- Client registration and reconnection
- Message sending and persistence
- SQLite message retrieval

You can use Python’s built-in `unittest` module for coverage.

---

## ✅ Future Improvements

- Add encryption (e.g., RSA for key exchange, AES for message encryption)
- Include chat history viewer in GUI
- Add WebSocket support for better scalability
- Group chat or file-sharing support

---

## 📄 License

MIT License (add your actual license file here)
