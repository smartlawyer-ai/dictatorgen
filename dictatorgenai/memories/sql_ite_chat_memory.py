import sqlite3
import uuid
from typing import List, Dict, Optional
from .base_chat_memory import BaseChatMemory

class SQLiteChatMemory(BaseChatMemory):
    """
    Implémentation de BaseChatMemory utilisant SQLite comme backend de stockage.
    """

    def __init__(self, db_path: str = "chat_memory.db"):
        """
        Initialise la base de données SQLite.

        Args:
            db_path (str): Chemin vers le fichier SQLite (par défaut: "chat_memory.db").
        """
        self.db_path = db_path
        self._create_table()

    def _get_connection(self):
        """
        Crée une nouvelle connexion SQLite pour chaque requête.
        """
        return sqlite3.connect(self.db_path, check_same_thread=False)

    def _create_table(self):
        """
        Crée une table SQLite pour stocker les messages si elle n'existe pas.
        """
        conn = self._get_connection()
        with conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS messages (
                    message_id TEXT PRIMARY KEY,
                    memory_id TEXT NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
        conn.close()

    def add_message(self, memory_id: str, message: Dict[str, str]) -> str:
        """
        Ajoute un message à la base de données SQLite avec un UUID.

        Args:
            memory_id (str): Identifiant de la discussion.
            message (Dict[str, str]): Message contenant le rôle et le contenu.

        Returns:
            str: L'UUID du message ajouté.
        """
        message_id = str(uuid.uuid4())
        conn = self._get_connection()
        with conn:
            conn.execute(
                "INSERT INTO messages (message_id, memory_id, role, content) VALUES (?, ?, ?, ?)",
                (message_id, memory_id, message["role"], message["content"]),
            )
        conn.close()
        return message_id

    def add_messages(self, memory_id: str, messages: List[Dict[str, str]]) -> List[str]:
        """
        Ajoute plusieurs messages à une discussion en une seule transaction.

        Args:
            memory_id (str): Identifiant de la discussion.
            messages (List[Dict[str, str]]): Liste des messages à ajouter.

        Returns:
            List[str]: Liste des UUID des messages ajoutés.
        """
        message_ids = []
        conn = self._get_connection()
        with conn:
            for message in messages:
                message_id = str(uuid.uuid4())
                message_ids.append(message_id)
                conn.execute(
                    "INSERT INTO messages (message_id, memory_id, role, content) VALUES (?, ?, ?, ?)",
                    (message_id, memory_id, message["role"], message["content"]),
                )
        conn.close()
        return message_ids

    def get_messages(self, memory_id: str) -> List[Dict[str, str]]:
        """
        Récupère tous les messages associés à un memory_id.

        Args:
            memory_id (str): Identifiant de la mémoire.

        Returns:
            List[Dict[str, str]]: Liste des messages sous forme de dictionnaires.
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT message_id, role, content, timestamp FROM messages WHERE memory_id = ? ORDER BY timestamp ASC",
            (memory_id,),
        )
        rows = cursor.fetchall()
        conn.close()
        return [
            {"message_id": row[0], "role": row[1], "content": row[2], "timestamp": row[3]}
            for row in rows
        ]

    def delete_memory(self, memory_id: str):
        """
        Supprime tous les messages associés à un memory_id.

        Args:
            memory_id (str): Identifiant de la mémoire à supprimer.
        """
        conn = self._get_connection()
        with conn:
            conn.execute("DELETE FROM messages WHERE memory_id = ?", (memory_id,))
        conn.close()

    def delete_message(self, memory_id: str, message_id: str) -> Optional[Dict[str, str]]:
        """
        Supprime un message spécifique d'une discussion.

        Args:
            memory_id (str): Identifiant unique de la discussion.
            message_id (str): UUID du message à supprimer.

        Returns:
            Optional[Dict[str, str]]: Le message supprimé, ou `None` s'il n'existe pas.
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT message_id, role, content, timestamp FROM messages WHERE memory_id = ? AND message_id = ?",
            (memory_id, message_id),
        )
        message = cursor.fetchone()

        if message:
            with conn:
                conn.execute("DELETE FROM messages WHERE message_id = ?", (message_id,))
            conn.close()
            return {"message_id": message[0], "role": message[1], "content": message[2], "timestamp": message[3]}

        conn.close()
        return None

    def delete_messages(self, memory_id: str, message_ids: List[str]) -> List[Dict[str, str]]:
        """
        Supprime plusieurs messages d'une discussion.

        Args:
            memory_id (str): Identifiant unique de la discussion.
            message_ids (List[str]): Liste des UUID des messages à supprimer.

        Returns:
            List[Dict[str, str]]: Liste des messages supprimés.
        """
        if not message_ids:
            return []

        conn = self._get_connection()
        cursor = conn.cursor()
        query = f"SELECT message_id, role, content, timestamp FROM messages WHERE memory_id = ? AND message_id IN ({','.join('?' * len(message_ids))})"
        cursor.execute(query, (memory_id, *message_ids))
        messages = cursor.fetchall()

        if messages:
            with conn:
                delete_query = f"DELETE FROM messages WHERE message_id IN ({','.join('?' * len(message_ids))})"
                conn.execute(delete_query, message_ids)
            conn.close()
            return [
                {"message_id": msg[0], "role": msg[1], "content": msg[2], "timestamp": msg[3]}
                for msg in messages
            ]

        conn.close()
        return []
