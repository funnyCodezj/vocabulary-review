"""Entry point for PyInstaller standalone exe and direct python start."""
import sys
import os
import threading
import time

# Ensure backend directory is in path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

import uvicorn
from app import app

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8004))
    host = os.environ.get("HOST", "0.0.0.0")
    url = f"http://localhost:{port}"

    # Open browser after server starts
    def _open_browser():
        time.sleep(1.5)
        try:
            import webbrowser
            webbrowser.open(url)
        except Exception:
            pass

    threading.Thread(target=_open_browser, daemon=True).start()

    print(f"Starting Vocabulary Review on {url}")
    uvicorn.run(app, host=host, port=port, reload=False)
