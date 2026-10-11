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
            import re
            msg = self.format(record)
            
            # Bersihkan escape sequence ANSI (contoh \033[40m\033[36m ... \033[0m)
            ansi_regex = re.compile(r'\x1b\[[0-9;]*[a-zA-Z]')
            clean_raw = ansi_regex.sub('', msg).strip()

            # Deteksi nama agent dari kurung siku awal, misal [Scanner Agent]
            agent_bracket_regex = re.compile(r'^\[([a-zA-Z0-9\s_.-]+)\]\s*(.*)$')
            known_levels = {"INFO", "WARNING", "WARN", "ERROR", "DEBUG", "CRITICAL"}
            
            agent_name = None
            clean_message = clean_raw

            match = agent_bracket_regex.match(clean_raw)
            if match:
                candidate = match.group(1).strip()
                if candidate.upper() not in known_levels:
                    agent_name = candidate
                    clean_message = match.group(2).strip()

            # Fallback jika agent belum terdeteksi dari kurung siku
            if not agent_name:
                rec_name = getattr(record, "name", "") or ""
                lower_msg = clean_raw.lower()
                if "scanner" in lower_msg:
                    agent_name = "Scanner Agent"
                elif "autonomous" in lower_msg or "planning" in lower_msg or "planner" in lower_msg:
                    agent_name = "Planning Agent"
                elif "ensemble" in lower_msg:
                    agent_name = "Ensemble Agent"
                elif "neural" in lower_msg or "pytorch" in lower_msg:
                    agent_name = "Neural Network Agent"
                elif "risk" in lower_msg:
                    agent_name = "Risk Analyst Agent"
                elif "specialist" in lower_msg:
                    agent_name = "Specialist Agent"
                elif "conversational" in lower_msg or "react" in lower_msg:
                    agent_name = "Conversational ReAct Agent"
                elif "frontier" in lower_msg:
                    agent_name = "Frontier Agent"
                elif "messaging" in lower_msg or "telegram" in lower_msg:
                    agent_name = "Messaging Agent"
                elif "preprocessor" in lower_msg:
                    agent_name = "Preprocessor Agent"
                elif rec_name.startswith("AutoBargain"):
                    agent_name = "AutoBargain"
                else:
                    agent_name = "System"

            final_message = clean_message if clean_message else clean_raw
            timestamp = datetime.fromtimestamp(record.created).strftime("%H:%M:%S")
            log_entry = {
                "timestamp": timestamp,
                "level": record.levelname,
                "agent": agent_name,
                "message": final_message,
                "raw": f"[{timestamp}] [{record.levelname}] [{agent_name}] {final_message}"
            }
            self.history.append(log_entry)

            # Broadcast ke subscriber async
            loop = self._loop
            if not loop or not loop.is_running():
                try:
                    loop = asyncio.get_running_loop()
                    self._loop = loop
                except RuntimeError:
                    pass

            if loop and loop.is_running():
                for queue in list(self.listeners):
                    try:
                        loop.call_soon_threadsafe(queue.put_nowait, log_entry)
                    except Exception:
                        pass
            else:
                for queue in list(self.listeners):
                    try:
                        queue.put_nowait(log_entry)
                    except Exception:
                        pass
        except Exception:
            self.handleError(record)

    def get_history(self, limit: int = 50) -> List[dict]:
        return list(self.history)[-limit:]

    def register_listener(self) -> asyncio.Queue:
        # Tangkap event loop aktif saat listener mendaftar
        if not self._loop or not self._loop.is_running():
            try:
                self._loop = asyncio.get_running_loop()
            except RuntimeError:
                pass
        q = asyncio.Queue(maxsize=300)
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
root_logger = logging.getLogger()
root_logger.addHandler(broadcast_handler)
if root_logger.level == logging.NOTSET or root_logger.level > logging.INFO:
    root_logger.setLevel(logging.INFO)
