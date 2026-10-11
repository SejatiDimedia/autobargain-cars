#!/bin/bash
# ==============================================================================
# AutoBargain Cars AI - Resume Project Script
# ==============================================================================
# Skrip ini otomatis memulihkan environment project (membuat ulang .venv,
# menginstal requirements.txt, dan menginstal node_modules) sehingga Anda
# dapat langsung melanjutkan pengembangan kapan saja dalam 1 klik.
# ==============================================================================

set -e
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_ROOT"

echo "🚗 [AutoBargain AI] Memulai pemulihan project (Resume)..."
echo "📂 Lokasi project: $PROJECT_ROOT"

# 1. Periksa ketersediaan Python & Node
command -v python3 >/dev/null 2>&1 || { echo "❌ python3 tidak ditemukan di sistem!"; exit 1; }
command -v npm >/dev/null 2>&1 || { echo "❌ npm tidak ditemukan di sistem!"; exit 1; }

# 2. Setup backend virtual environment
echo ""
echo "🐍 [1/3] Menyiapkan backend Python virtual environment (.venv)..."
if [ ! -d "backend/.venv" ]; then
    echo "   -> Membuat virtualenv baru di backend/.venv..."
    python3 -m venv backend/.venv
fi

echo "   -> Menginstal dependencies dari requirements.txt..."
backend/.venv/bin/pip install --upgrade pip --quiet
backend/.venv/bin/pip install -r backend/requirements.txt --quiet
echo "   -> Backend dependencies berhasil dipulihkan."

# 3. Setup frontend dependencies
echo ""
echo "⚛️ [2/3] Menyiapkan frontend node_modules..."
if [ ! -d "frontend/node_modules" ]; then
    echo "   -> Menjalankan npm install di frontend/..."
    cd frontend && npm install --silent && cd ..
fi
echo "   -> Frontend dependencies berhasil dipulihkan."

# 4. Selesai
echo ""
echo "🎉 [3/3] Pemulihan selesai 100%!"
echo ""
echo "=============================================================================="
echo "🚀 CARA MENJALANKAN KEMBALI APLIKASI:"
echo "1. Jalankan Backend API:"
echo "   backend/.venv/bin/python backend/run.py"
echo ""
echo "2. Jalankan Frontend UI (di terminal terpisah):"
echo "   cd frontend && npm run dev"
echo ""
echo "3. Buka di browser: http://localhost:5173"
echo "=============================================================================="
