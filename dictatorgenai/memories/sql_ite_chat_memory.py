import sqlite3
from typing import List, Dict

class SQLiteChatMemory:
    """
    Implémentation de ChatMemory utilisant SQLite comme backend de stockage.
    """

    def __init__(self, db_path: str = "chat_memory.db"):
        """
        Initialise une connexion SQLite et configure la base de données.

        Args:
            db_path (str): Chemin vers le fichier SQLite (par défaut: "chat_memory.db").
        """
        self.db_path = db_path
        self.conn = sqlite3.connect(self.db_path)
        self._create_table()

    def _create_table(self):
        """
        Crée une table SQLite pour stocker les messages si elle n'existe pas.
        """
        with self.conn:
            self.conn.execute(
                """
                CREATE TABLE IF NOT EXISTS messages (
                    memory_id TEXT NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
                """
            )

    def add_message(self, memory_id: str, message: Dict[str, str]):
        """
        Ajoute un message à la base de données SQLite.

        Args:
            memory_id (str): Identifiant de la mémoire.
            message (Dict[str, str]): Dictionnaire contenant le rôle et le contenu du message.
        """
        with self.conn:
            self.conn.execute(
                "INSERT INTO messages (memory_id, role, content) VALUES (?, ?, ?)",
                (memory_id, message["role"], message["content"]),
            )

    def get_messages(self, memory_id: str) -> List[Dict[str, str]]:
        """
        Récupère tous les messages associés à un memory_id.

        Args:
            memory_id (str): Identifiant de la mémoire.

        Returns:
            List[Dict[str, str]]: Liste des messages sous forme de dictionnaires.
        """
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT role, content, timestamp FROM messages WHERE memory_id = ? ORDER BY timestamp ASC",
            (memory_id,),
        )
        rows = cursor.fetchall()
        return [{"role": row[0], "content": row[1], "timestamp": row[2]} for row in rows]

    def delete_memory(self, memory_id: str):
        """
        Supprime tous les messages associés à un memory_id.

        Args:
            memory_id (str): Identifiant de la mémoire à supprimer.
        """
        with self.conn:
            self.conn.execute("DELETE FROM messages WHERE memory_id = ?", (memory_id,))

    def close(self):
        """
        Ferme la connexion SQLite.
        """
        self.conn.close()
