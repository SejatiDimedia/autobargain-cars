import sys
from pathlib import Path

# Add backend directory to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import time
import signal
import argparse
from datetime import datetime
from dotenv import load_dotenv
from car_agent_framework import CarAgentFramework

load_dotenv(override=True)


class AutoBargainScheduler:
    """
    Autonomous background worker daemon that periodically triggers the multi-agent
    arbitrage scanning pipeline and dispatches Telegram push alerts 24/7.
    """

    def __init__(self, interval_seconds: int = 300, use_autonomous_agent: bool = False):
        self.interval_seconds = interval_seconds
        self.use_autonomous = use_autonomous_agent
        self.running = True
        self.framework = CarAgentFramework()
        self.cycle_count = 0

        # Handle graceful shutdown on Ctrl+C / SIGINT
        signal.signal(signal.SIGINT, self._handle_exit)
        signal.signal(signal.SIGTERM, self._handle_exit)

    def _handle_exit(self, signum, frame):
        print("\n\n🛑 [AutoBargain Scheduler] Menerima sinyal berhenti. Menutup daemon dengan aman...")
        self.running = False
        sys.exit(0)

    def run_single_cycle(self):
        self.cycle_count += 1
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"\n{'='*70}")
        print(f"⏰ [{now_str}] Memulai Siklus Arbitrase #{self.cycle_count}")
        print(f"{'='*70}")

        try:
            # Jalankan satu siklus penuh multi-agent framework
            memory_deals = self.framework.run()
            
            print(f"✅ Siklus #{self.cycle_count} selesai sukses.")
            print(f"📊 Total database peluang tersimpan saat ini: {len(memory_deals)} mobil.")
            if memory_deals:
                top = memory_deals[0]
                print(f"🔥 Peluang Terkini: {top.deal.brand} {top.deal.model} ({top.deal.year}) | Profit Gap: Rp {top.discount:.1f} Jt")
        except Exception as e:
            print(f"⚠️ [Error Siklus #{self.cycle_count}]: {e}")

    def start(self):
        interval_min = self.interval_seconds / 60
        print("\n" + "="*70)
        print("🚗 [AUTOBARGAIN AI] AUTONOMOUS SCHEDULER DAEMON RUNNING")
        print(f"📡 Interval Scan   : Setiap {self.interval_seconds} detik ({interval_min:.1f} menit)")
        print(f"🤖 Planner Mode    : {'ReAct Autonomous Agent' if self.use_autonomous else 'Deterministic Ensemble Planner'}")
        print("📱 Telegram Alert  : Aktif (Auto push saat profit >= Rp 20 Juta)")
        print("💡 Tekan Ctrl+C untuk menghentikan daemon kapan saja.")
        print("="*70 + "\n")

        # Jalankan siklus pertama segera
        self.run_single_cycle()

        while self.running:
            try:
                next_run = datetime.fromtimestamp(time.time() + self.interval_seconds).strftime("%H:%M:%S")
                print(f"\n💤 Menunggu jadwal berikutnya pada pukul {next_run} ({self.interval_seconds} detik)...")
                time.sleep(self.interval_seconds)
                if self.running:
                    self.run_single_cycle()
            except KeyboardInterrupt:
                self._handle_exit(None, None)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AutoBargain AI Background Scheduler Daemon")
    parser.add_argument(
        "--interval",
        "-i",
        type=int,
        default=5,
        help="Interval scan dalam MENIT (default: 5 menit)",
    )
    parser.add_argument(
        "--seconds",
        "-s",
        type=int,
        default=None,
        help="Interval scan dalam DETIK (opsional jika ingin lebih cepat untuk testing)",
    )
    parser.add_argument(
        "--autonomous",
        action="store_true",
        help="Gunakan ReAct Autonomous Planning Agent daripada Deterministic Planner",
    )
    parser.add_argument(
        "--bot",
        "-b",
        action="store_true",
        help="Jalankan juga Interactive Telegram Bot (/scan, /deals, /stats) di background",
    )

    args = parser.parse_args()

    interval_sec = args.seconds if args.seconds is not None else (args.interval * 60)

    if args.bot:
        import threading
        from telegram_bot import InteractiveTelegramBot
        print("🤖 [Interactive Telegram Bot] Memulai listener di thread background...")
        bot = InteractiveTelegramBot()
        bot_thread = threading.Thread(target=bot.run_polling, daemon=True)
        bot_thread.start()

    scheduler = AutoBargainScheduler(
        interval_seconds=interval_sec,
        use_autonomous_agent=args.autonomous
    )
    scheduler.start()
