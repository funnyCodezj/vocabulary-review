import os
import sys
from dotenv import load_dotenv

# In PyInstaller bundle, code runs from temp dir (_MEIPASS)
# but we want the database and user data to be near the exe
if getattr(sys, "frozen", False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

CODE_DIR = os.path.dirname(os.path.abspath(__file__))

load_dotenv(os.path.join(CODE_DIR, ".env"))
DATABASE_URL = f"sqlite:///{os.path.join(BASE_DIR, 'vocab.db')}"
AUDIO_DIR = os.path.join(BASE_DIR, "audio")
IMAGE_DIR = os.path.join(BASE_DIR, "images")

os.makedirs(AUDIO_DIR, exist_ok=True)
os.makedirs(IMAGE_DIR, exist_ok=True)

# Free Dictionary API
DICTIONARY_API_BASE = "https://api.dictionaryapi.dev/api/v2/entries/en"

# Image API keys (free tiers)
PEXELS_API_KEY = os.getenv("PEXELS_API_KEY", "")
UNSPLASH_ACCESS_KEY = os.getenv("UNSPLASH_ACCESS_KEY", "")
