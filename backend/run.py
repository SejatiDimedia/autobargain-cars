import uvicorn
import sys
from pathlib import Path

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

if __name__ == "__main__":
    print("🚗 Starting AutoBargain Cars AI API Server on http://127.0.0.1:8000 ...")
    print("📚 API Documentation available at http://127.0.0.1:8000/docs")
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
