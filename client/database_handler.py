import sqlite3
from datetime import datetime

class DatabaseHandler:
    def __init__(self, username=None, db_path=None):
        if db_path is None and username is not None:
            db_path = f"chat_{username}.db"
        self.db_path = db_path or "client_chat.db"
        self._create_tables()

    def _connect(self):
        return sqlite3.connect(self.db_path)

    def _create_tables(self):
        with self._connect() as conn:
            cursor = conn.cursor()

            # Client Info
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS client_info (
                    client_id TEXT PRIMARY KEY,
                    username TEXT,
                    p2p_host TEXT,
                    p2p_port INTEGER
                )
            """)

            # Other Clients
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS other_clients (
                    client_id TEXT PRIMARY KEY,
                    username TEXT,
                    p2p_host TEXT,
                    p2p_port INTEGER,
                    relation TEXT
                )
            """)

            # Messages
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    sender TEXT,
                    receiver TEXT,
                    message TEXT,
                    timestamp TEXT
                )
            """)

            conn.commit()

    # === Client Info ===
    def save_client_info(self, client_id, username, host, port):
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO client_info (client_id, username, p2p_host, p2p_port)
                VALUES (?, ?, ?, ?)
            """, (client_id, username, host, port))
            conn.commit()

    def load_client_info(self):
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT client_id, username, p2p_host, p2p_port FROM client_info LIMIT 1")
            return cursor.fetchone()

    # === Other Clients ===
    def upsert_other_client(self, client_id, username, host, port, relation):
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO other_clients (client_id, username, p2p_host, p2p_port, relation)
                VALUES (?, ?, ?, ?, ?)
            """, (client_id, username, host, port, relation))
            conn.commit()

    def get_all_other_clients(self):
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT client_id, username, p2p_host, p2p_port, relation FROM other_clients")
            return cursor.fetchall()

    # === Messages ===
    def save_message(self, sender, receiver, message, timestamp=None):
        timestamp = timestamp or datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO messages (sender, receiver, message, timestamp)
                VALUES (?, ?, ?, ?)
            """, (sender, receiver, message, timestamp))
            conn.commit()

    def get_chat_history(self, user1, user2):
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT sender, receiver, message, timestamp
                FROM messages
                WHERE (sender=? AND receiver=?) OR (sender=? AND receiver=?)
                ORDER BY timestamp
            """, (user1, user2, user2, user1))
            return cursor.fetchall()