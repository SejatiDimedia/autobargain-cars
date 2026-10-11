#!/bin/bash
# ==============================================================================
# AutoBargain Cars AI - Pause & Free Up Resources Script
# ==============================================================================
# Skrip ini membersihkan dependency berat (.venv ~1.8GB & node_modules ~145MB)
# serta file cache sementara saat project di-pause.
# Seluruh source code, data memori mobil (cars_memory.json), dan database vektor
# (cars_vectorstore) TETAP AMAN 100% dan tidak akan dihapus.
# ==============================================================================

set -e
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_ROOT"

echo "🚗 [AutoBargain AI] Memulai proses Pause & Penghematan Resource..."
echo "📂 Lokasi project: $PROJECT_ROOT"

# 1. Hentikan proses server yang mungkin masih berjalan di background
echo ""
echo "🛑 [1/4] Memeriksa & menghentikan proses server aktif..."
PORT_8000_PID=$(lsof -ti :8000 2>/dev/null || true)
if [ -n "$PORT_8000_PID" ]; then
    echo "   -> Menghentikan FastAPI backend (PID: $PORT_8000_PID)..."
    kill -9 $PORT_8000_PID 2>/dev/null || true
fi

PORT_5173_PID=$(lsof -ti :5173 2>/dev/null || true)
if [ -n "$PORT_5173_PID" ]; then
    echo "   -> Menghentikan Vite dev server (PID: $PORT_5173_PID)..."
    kill -9 $PORT_5173_PID 2>/dev/null || true
fi
echo "   -> Server background bersih (0% RAM / CPU terpakai)."

# 2. Hapus cache Python bytecode dan .DS_Store
echo ""
echo "🧹 [2/4] Membersihkan cache Python & temporary files..."
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -type f -name "*.pyc" -delete 2>/dev/null || true
find . -type f -name ".DS_Store" -delete 2>/dev/null || true
rm -rf frontend/dist 2>/dev/null || true
echo "   -> Cache sementara berhasil dibersihkan."

# 3. Hapus dependency berat (.venv dan node_modules)
echo ""
echo "📦 [3/4] Menghapus virtual environment & node_modules (hemat ~1.95 GB)..."
if [ -d "backend/.venv" ]; then
    rm -rf backend/.venv
    echo "   -> backend/.venv (1.8 GB) berhasil dihapus."
fi

if [ -d "frontend/node_modules" ]; then
    rm -rf frontend/node_modules
    echo "   -> frontend/node_modules (145 MB) berhasil dihapus."
fi

# 4. Ringkasan ukuran project setelah dibersihkan
echo ""
echo "📊 [4/4] Menghitung ukuran akhir project:"
TOTAL_SIZE=$(du -sh . 2>/dev/null | awk '{print $1}')
echo "   -> Ukuran project sekarang: $TOTAL_SIZE (sebelumnya ~1.95 GB)."
echo ""
echo "✅ SUKSES! Project AutoBargain Cars AI sekarang dalam status PAUSED & SUPER RINGAN."
echo "💡 Kapan pun Anda ingin melanjutkan project ini kembali, cukup jalankan:"
echo "   ./resume_project.sh"
echo "=============================================================================="
