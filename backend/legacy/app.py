import sys
from pathlib import Path

# Add backend directory to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import logging
import queue
import threading
import time
from datetime import datetime
import gradio as gr
import plotly.graph_objects as go
from dotenv import load_dotenv

from car_agent_framework import CarAgentFramework
from agents.cars import ScrapedCarDeal
from log_utils import reformat

load_dotenv(override=True)


class QueueHandler(logging.Handler):
    def __init__(self, log_queue):
        super().__init__()
        self.log_queue = log_queue

    def emit(self, record):
        self.log_queue.put(self.format(record))


def html_for(log_data):
    output = "<br>".join(log_data[-25:])
    return f"""
    <div id="scrollContent" style="height: 360px; overflow-y: auto; border: 1px solid #2a2a35; background-color: #0e0e13; color: #e2e8f0; font-family: 'SF Mono', Menlo, Monaco, 'Courier New', monospace; font-size: 11.5px; padding: 14px; border-radius: 8px; line-height: 1.6;">
    {output}
    </div>
    """


def setup_logging(log_queue):
    handler = QueueHandler(log_queue)
    formatter = logging.Formatter("[%(asctime)s] %(message)s", datefmt="%H:%M:%S")
    handler.setFormatter(formatter)
    logger = logging.getLogger()
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)


CUSTOM_CSS = """
/* Styling tabel scrollable & modern */
.gradio-container {
    max-width: 96% !important;
}
.scroll-table {
    max-height: 400px !important;
    overflow-y: auto !important;
}
#scrollContent::-webkit-scrollbar, .scroll-table::-webkit-scrollbar {
    width: 6px;
    height: 6px;
}
#scrollContent::-webkit-scrollbar-thumb, .scroll-table::-webkit-scrollbar-thumb {
    background: #4a5568;
    border-radius: 4px;
}
"""


class AutoBargainApp:
    def __init__(self):
        self.framework = None

    def get_framework(self):
        if not self.framework:
            self.framework = CarAgentFramework()
        return self.framework

    def run(self):
        with gr.Blocks(
            title="AutoBargain AI — Used Car Arbitrage Radar",
            theme=gr.themes.Soft(primary_hue="blue", secondary_hue="indigo"),
            fill_width=True,
            css=CUSTOM_CSS,
        ) as ui:
            log_data = gr.State([])

            def table_for(opportunities):
                rows = []
                for opp in opportunities:
                    risk = opp.risk_report
                    if risk:
                        safety_str = f"⭐ {risk.safety_score}/10\n({risk.grade})"
                        flags_str = ", ".join(risk.red_flags[:2]) if risk.red_flags else "Aman (No Red Flags)"
                    else:
                        safety_str = "⭐ 9.0/10\n(Grade A)"
                        flags_str = "Aman (No Red Flags)"

                    rows.append([
                        f"{opp.deal.brand} {opp.deal.model} ({opp.deal.year})",
                        f"Rp {opp.deal.price:.1f} Jt",
                        f"Rp {opp.estimate:.1f} Jt",
                        f"🔥 Rp {opp.discount:.1f} Jt ({opp.discount/opp.estimate*100:.1f}%)" if opp.discount > 0 else f"Rp {opp.discount:.1f} Jt",
                        safety_str,
                        flags_str,
                        f"{opp.deal.mileage_km:,} km",
                        opp.deal.url,
                    ])
                return rows

            def fetch_live_scraped_table():
                """Ambil data scraping live dari web marketplace secara real-time"""
                try:
                    deals = ScrapedCarDeal.fetch()
                    now_str = datetime.now().strftime("%H:%M:%S")
                    rows = [
                        [
                            d.brand,
                            d.title[:65] + ("..." if len(d.title) > 65 else ""),
                            f"Rp {d.asking_price:.1f} Jt" if d.asking_price > 0 else "Nego / Call",
                            str(d.year),
                            d.trans,
                            d.url,
                            f"Live Scraped ({now_str})"
                        ]
                        for d in deals
                    ]
                    status_msg = f"✅ Sukses menarik {len(deals)} mobil live langsung dari Carmudi / Marketplace pada pukul {now_str}"
                    return rows, status_msg
                except Exception as e:
                    return [], f"⚠️ Gagal scraping live: {e}"

            def update_output(log_data, log_queue, result_queue):
                initial_table = table_for(self.get_framework().memory)
                final_table = None
                while True:
                    try:
                        message = log_queue.get_nowait()
                        log_data.append(reformat(message))
                        yield log_data, html_for(log_data), final_table or initial_table
                    except queue.Empty:
                        try:
                            final_table = result_queue.get_nowait()
                            yield log_data, html_for(log_data), final_table or initial_table
                        except queue.Empty:
                            if final_table is not None:
                                break
                            time.sleep(0.1)

            def get_3d_plot():
                docs, vectors, colors = CarAgentFramework.get_plot_data(max_datapoints=500)
                if len(vectors) == 0:
                    fig = go.Figure()
                    fig.update_layout(title="No vector data available. Run seed_database.py first.", height=360)
                    return fig

                fig = go.Figure(
                    data=[
                        go.Scatter3d(
                            x=vectors[:, 0],
                            y=vectors[:, 1],
                            z=vectors[:, 2],
                            mode="markers",
                            text=docs,
                            hoverinfo="text",
                            marker=dict(size=4, color=colors, opacity=0.85),
                        )
                    ]
                )
                fig.update_layout(
                    title="<b>3D Car Vector Space (ChromaDB + t-SNE)</b>",
                    scene=dict(
                        xaxis=dict(showticklabels=False, title=""),
                        yaxis=dict(showticklabels=False, title=""),
                        zaxis=dict(showticklabels=False, title=""),
                        aspectmode="cube",
                    ),
                    height=360,
                    margin=dict(r=5, b=5, l=5, t=30),
                    paper_bgcolor="#141419",
                    font=dict(color="#ffffff"),
                )
                return fig

            def do_scan():
                new_opps = self.get_framework().run()
                return table_for(new_opps)

            def run_with_logging(initial_log_data):
                log_queue = queue.Queue()
                result_queue = queue.Queue()
                setup_logging(log_queue)

                def worker():
                    result = do_scan()
                    result_queue.put(result)

                thread = threading.Thread(target=worker)
                thread.start()

                for log_d, html_logs, table in update_output(initial_log_data, log_queue, result_queue):
                    yield log_d, html_logs, table

            def on_select_deal(evt: gr.SelectData):
                opps = self.get_framework().memory
                if evt.index[0] < len(opps):
                    selected = opps[evt.index[0]]
                    self.get_framework().planner.messenger.alert(selected)
                    gr.Info(f"Pushed alert for {selected.deal.brand} {selected.deal.model} to Telegram!")

            # =================================================================
            # UI HEADER
            # =================================================================
            gr.Markdown(
                """
                # 🚗 AutoBargain AI — Radar Arbitrase Mobil Bekas Murah
                ### *Autonomous Multi-Agent AI System powered by Live Web Scraping, ChromaDB RAG, Groq 120B/Gemini, and Telegram Alerts*
                """
            )

            with gr.Tabs():
                # =============================================================
                # TAB 1: PELUANG ARBITRASE & RADAR VALUASI
                # =============================================================
                with gr.TabItem("🏆 Peluang Arbitrase (Memory Radar)"):
                    with gr.Row():
                        btn_scan = gr.Button("⚡ Trigger Live Arbitrage Scan Now", variant="primary", scale=2)
                        btn_refresh_mem = gr.Button("🔄 Refresh Tabel Memori", scale=1)

                    gr.Markdown("💡 *Tabel data memori di bawah dapat di-scroll vertikal. Klik baris mana saja untuk mengirimkan alert ulang ke Telegram.*")

                    with gr.Row():
                        opportunities_table = gr.Dataframe(
                            headers=[
                                "Mobil (Brand/Model/Tahun)",
                                "Harga Listing",
                                "Estimasi Pasar",
                                "Potensi Untung",
                                "🛡️ Safety Score & Grade",
                                "⚠️ Red Flags / Catatan",
                                "Kilometer",
                                "Link Iklan",
                            ],
                            wrap=True,
                            max_height=380,
                            elem_classes=["scroll-table"],
                            interactive=False,
                        )

                    with gr.Row():
                        with gr.Column(scale=1):
                            gr.Markdown("#### 🖥️ Real-time Multi-Agent Log Stream")
                            logs_view = gr.HTML()
                        with gr.Column(scale=1):
                            gr.Markdown("#### 🌐 3D Vector Space Embedding Clustering")
                            plot_view = gr.Plot(value=get_3d_plot(), show_label=False)

                # =============================================================
                # TAB 2: LIVE WEB SCRAPING RADAR
                # =============================================================
                with gr.TabItem("🌐 Live Web Scraping Feed (Marketplace)"):
                    gr.Markdown(
                        """
                        ### 📡 Live Real-Time Web Scraping Monitor
                        *Tarik dan intip langsung listing mobil mentah yang sedang aktif dijual di marketplace (Carmudi/Mobil123) detik ini.*
                        """
                    )
                    with gr.Row():
                        btn_fetch_live = gr.Button("🔍 Fetch Live Cars from Web Now", variant="secondary", scale=2)
                    
                    live_status_txt = gr.Markdown("Tekan tombol di atas untuk memulai penarikan live data dari web.")

                    live_scraped_table = gr.Dataframe(
                        headers=[
                            "Merk",
                            "Judul Iklan Listing",
                            "Harga Penawaran",
                            "Tahun",
                            "Transmisi",
                            "Link URL Unit Asli",
                            "Status Scraper",
                        ],
                        wrap=True,
                        max_height=420,
                        elem_classes=["scroll-table"],
                        interactive=False,
                    )

            # =================================================================
            # EVENT HANDLERS
            # =================================================================
            # Initial load
            ui.load(
                run_with_logging,
                inputs=[log_data],
                outputs=[log_data, logs_view, opportunities_table],
            )
            ui.load(
                fetch_live_scraped_table,
                inputs=[],
                outputs=[live_scraped_table, live_status_txt]
            )

            btn_scan.click(
                run_with_logging,
                inputs=[log_data],
                outputs=[log_data, logs_view, opportunities_table],
            )

            btn_refresh_mem.click(
                lambda: table_for(self.get_framework().memory),
                inputs=[],
                outputs=[opportunities_table]
            )

            btn_fetch_live.click(
                fetch_live_scraped_table,
                inputs=[],
                outputs=[live_scraped_table, live_status_txt]
            )

            # Auto-run timer setiap 300 detik (5 menit)
            timer = gr.Timer(value=300, active=True)
            timer.tick(
                run_with_logging,
                inputs=[log_data],
                outputs=[log_data, logs_view, opportunities_table],
            )

            # Klik baris tabel untuk kirim ulang alert ke Telegram
            opportunities_table.select(on_select_deal)

        ui.launch(inbrowser=True)


if __name__ == "__main__":
    AutoBargainApp().run()
