import logging
import asyncio
from collections import deque
from typing import List, Set
from datetime import datetime

class BroadcastLogHandler(logging.Handler):
    """
    Handler logging kustom yang menyimpan riwayat log terbaru dalam buffer
    dan menyiarkan (broadcast) log secara real-time ke semua klien SSE / WebSocket aktif.
    """
    def __init__(self, max_history: int = 200):
        super().__init__()
        self.history = deque(maxlen=max_history)
        self.listeners: Set[asyncio.Queue] = set()
        self._loop: asyncio.AbstractEventLoop | None = None

    def set_event_loop(self, loop: asyncio.AbstractEventLoop):
        self._loop = loop

    def emit(self, record: logging.LogRecord):
        try:
            msg = self.format(record)
            timestamp = datetime.fromtimestamp(record.created).strftime("%H:%M:%S")
            log_entry = {
                "timestamp": timestamp,
                "level": record.levelname,
                "message": msg,
                "raw": f"[{timestamp}] [{record.levelname}] {msg}"
            }
            self.history.append(log_entry)

            # Broadcast ke subscriber async jika event loop aktif
            if self._loop and self._loop.is_running():
                for queue in list(self.listeners):
                    try:
                        self._loop.call_soon_threadsafe(queue.put_nowait, log_entry)
                    except Exception:
                        pass
        except Exception:
            self.handleError(record)

    def get_history(self, limit: int = 50) -> List[dict]:
        return list(self.history)[-limit:]

    def register_listener(self) -> asyncio.Queue:
        q = asyncio.Queue(maxsize=100)
        self.listeners.add(q)
        return q

    def unregister_listener(self, q: asyncio.Queue):
        self.listeners.discard(q)

# Global broadcast logger instance
broadcast_handler = BroadcastLogHandler()
formatter = logging.Formatter("%(message)s")
broadcast_handler.setFormatter(formatter)
broadcast_handler.setLevel(logging.INFO)

# Attach ke root logger
logging.getLogger().addHandler(broadcast_handler)
