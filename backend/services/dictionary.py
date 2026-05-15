import httpx
from typing import Optional, Dict

from config import DICTIONARY_API_BASE


MYMEMORY_API = "https://api.mymemory.translated.net/get"


async def fetch_chinese_translation(word: str) -> str:
    """Fetch Chinese translation via MyMemory API (free, no key needed)."""
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(
                MYMEMORY_API,
                params={"q": word, "langpair": "en|zh-CN"},
            )
            if resp.status_code == 200:
                data = resp.json()
                translated = data.get("responseData", {}).get("translatedText", "")
                if translated and translated.lower() != word.lower():
                    return translated
    except Exception:
        pass
    return ""


async def fetch_word_data(word: str) -> Optional[Dict]:
    """Fetch word data from Free Dictionary API.
    Returns parsed data or None if not found.
    """
    url = f"{DICTIONARY_API_BASE}/{word}"
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(url)
        if resp.status_code != 200:
            return None

        data = resp.json()
        if not data:
            return None

        entry = data[0]
        result = {
            "word": entry.get("word", word),
            "phonetic": "",
            "meanings": [],
        }

        # find first US phonetic
        if "phonetics" in entry:
            for p in entry["phonetics"]:
                if p.get("audio", "").endswith(".mp3"):
                    result["phonetic"] = p.get("text", "")
                    break
            if not result["phonetic"]:
                result["phonetic"] = entry.get("phonetic", "")

        # extract meanings
        for m in entry.get("meanings", []):
            meaning = {
                "partOfSpeech": m.get("partOfSpeech", ""),
                "definitions": [],
            }
            for d in m.get("definitions", [])[:2]:  # max 2 definitions per POS
                meaning["definitions"].append({
                    "definition": d.get("definition", ""),
                    "example": d.get("example", ""),
                })
            result["meanings"].append(meaning)

        return result
