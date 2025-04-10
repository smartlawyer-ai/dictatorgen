# mon_framework/memory_store/sqlite_store.py
import sqlite3
import json
from typing import List
from ...steps.base_step import TaskStep
from .memory_store import MemoryStore

class SQLiteStore(MemoryStore):
    """
    Implémente MemoryStore avec SQLite pour la persistance des étapes.
    """

    def __init__(self, db_path: str = "regime_memory.db"):
        """
        Initialise la base de données SQLite et crée les tables si elles n'existent pas.

        Args:
            db_path (str): Chemin du fichier de base de données SQLite.
        """
        self.db_path = db_path
        self._initialize_db()

    def _initialize_db(self):
        """Crée la table pour stocker les `TaskStep` si elle n'existe pas."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS memory_steps (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    memory_id TEXT NOT NULL,
                    step_data TEXT NOT NULL
                )
            """)
            conn.commit()

    def save_step(self, memory_id: str, step: TaskStep):
        """
        Sauvegarde une étape en JSON dans SQLite.

        Args:
            memory_id (str): Identifiant unique de la mémoire.
            step (TaskStep): Étape à sauvegarder.
        """
        step_data = json.dumps(step.to_dict())  # Convertit l'objet `TaskStep` en JSON
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO memory_steps (memory_id, step_data) VALUES (?, ?)", (memory_id, step_data))
            conn.commit()

    def load_steps(self, memory_id: str) -> List[TaskStep]:
        """
        Charge toutes les étapes d'une mémoire en JSON et les reconstruit en `TaskStep`.

        Args:
            memory_id (str): Identifiant de la mémoire.

        Returns:
            List[TaskStep]: Liste des étapes rechargées.
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT step_data FROM memory_steps WHERE memory_id = ?", (memory_id,))
            steps_json = cursor.fetchall()

        return [TaskStep.from_dict(json.loads(step[0])) for step in steps_json if step[0]] if steps_json else []

    def clear_memory(self, memory_id: str):
        """
        Supprime toutes les étapes d'une mémoire.

        Args:
            memory_id (str): Identifiant unique de la mémoire.
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM memory_steps WHERE memory_id = ?", (memory_id,))
            conn.commit()
