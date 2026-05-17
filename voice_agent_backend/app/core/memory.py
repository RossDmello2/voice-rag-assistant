from threading import Lock
from typing import Optional
import time


class SessionMemory:
    """
    Manages per-session conversation history and retrieval context.
    Replicates the committed memory system from script.js STATE.memory
    """

    def __init__(self, max_pairs: int = 10):
        self._sessions: dict[str, dict] = {}
        self._lock = Lock()
        self.max_pairs = max_pairs

    def get_or_create(self, session_id: str) -> dict:
        with self._lock:
            if session_id not in self._sessions:
                self._sessions[session_id] = {
                    "messages": [],           # [{role, content}]
                    "last_retrieval": {},     # last RAG result for follow-up context
                    "active_collection": "",
                    "language": "en",
                    "created_at": time.time(),
                    "updated_at": time.time(),
                }
            return self._sessions[session_id]

    def append_turn(self, session_id: str, user_text: str, assistant_text: str):
        session = self.get_or_create(session_id)
        with self._lock:
            session["messages"].append({"role": "user", "content": user_text})
            session["messages"].append({"role": "assistant", "content": assistant_text})
            # Rolling window: keep last max_pairs * 2 messages
            max_msgs = self.max_pairs * 2
            if len(session["messages"]) > max_msgs:
                session["messages"] = session["messages"][-max_msgs:]
            session["updated_at"] = time.time()

    def get_history(self, session_id: str) -> list[dict]:
        return self.get_or_create(session_id)["messages"]

    def set_last_retrieval(self, session_id: str, retrieval: dict):
        session = self.get_or_create(session_id)
        with self._lock:
            session["last_retrieval"] = retrieval

    def get_last_retrieval(self, session_id: str) -> dict:
        return self.get_or_create(session_id).get("last_retrieval", {})

    def clear(self, session_id: str):
        with self._lock:
            self._sessions.pop(session_id, None)

    def set_language(self, session_id: str, language: str):
        session = self.get_or_create(session_id)
        with self._lock:
            session["language"] = language

    def get_language(self, session_id: str) -> str:
        return self.get_or_create(session_id).get("language", "en")

    def set_active_collection(self, session_id: str, collection: str):
        session = self.get_or_create(session_id)
        with self._lock:
            session["active_collection"] = collection

    def get_active_collection(self, session_id: str) -> str:
        return self.get_or_create(session_id).get("active_collection", "")


memory_store = SessionMemory(max_pairs=10)
