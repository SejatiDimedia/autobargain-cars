import sqlite3
import os
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent.parent.parent
DB_FILE = BACKEND_DIR / "chat_history.db"


class ChatStorage:
    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = db_path or DB_FILE
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        with self._get_connection() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS chat_messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                """
            )
            conn.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_chat_messages_session 
                ON chat_messages(session_id, id ASC);
                """
            )
            conn.commit()

    def add_message(
        self, session_id: str, role: str, content: str, timestamp: Optional[str] = None
    ) -> Dict[str, Any]:
        ts = timestamp or datetime.now().strftime("%H:%M")
        with self._get_connection() as conn:
            cursor = conn.execute(
                """
                INSERT INTO chat_messages (session_id, role, content, timestamp)
                VALUES (?, ?, ?, ?)
                """,
                (session_id, role, content, ts),
            )
            conn.commit()
            msg_id = cursor.lastrowid
            return {
                "id": msg_id,
                "session_id": session_id,
                "role": role,
                "content": content,
                "timestamp": ts,
            }

    def get_messages(self, session_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.execute(
                """
                SELECT id, session_id, role, content, timestamp, created_at
                FROM chat_messages
                WHERE session_id = ?
                ORDER BY id ASC
                LIMIT ?
                """,
                (session_id, limit),
            )
            rows = cursor.fetchall()
            return [
                {
                    "id": r["id"],
                    "session_id": r["session_id"],
                    "role": r["role"],
                    "content": r["content"],
                    "timestamp": r["timestamp"],
                }
                for r in rows
            ]

    def clear_history(self, session_id: str) -> int:
        with self._get_connection() as conn:
            cursor = conn.execute(
                "DELETE FROM chat_messages WHERE session_id = ?", (session_id,)
            )
            conn.commit()
            return cursor.rowcount


chat_storage = ChatStorage()
