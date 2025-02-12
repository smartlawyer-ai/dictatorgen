import sqlite3
from typing import List, Dict

class SQLiteChatMemory:
    """
    Implémentation de ChatMemory utilisant SQLite comme backend de stockage.
    """

    def __init__(self, db_path: str = "chat_memory.db"):
        """
        Initialise la base de données SQLite.
        
        Args:
            db_path (str): Chemin vers le fichier SQLite (par défaut: "chat_memory.db").
        """
        self.db_path = db_path
        self._create_table()  # Création de la table une seule fois

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
                    memory_id TEXT NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
        conn.close()

    def add_message(self, memory_id: str, message: Dict[str, str]):
        """
        Ajoute un message à la base de données SQLite.

        Args:
            memory_id (str): Identifiant de la mémoire.
            message (Dict[str, str]): Dictionnaire contenant le rôle et le contenu du message.
        """
        conn = self._get_connection()
        with conn:
            conn.execute(
                "INSERT INTO messages (memory_id, role, content) VALUES (?, ?, ?)",
                (memory_id, message["role"], message["content"]),
            )
        conn.close()

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
            "SELECT role, content, timestamp FROM messages WHERE memory_id = ? ORDER BY timestamp ASC",
            (memory_id,),
        )
        rows = cursor.fetchall()
        conn.close()
        return [{"role": row[0], "content": row[1], "timestamp": row[2]} for row in rows]

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
