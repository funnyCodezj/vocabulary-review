import json, httpx
from typing import Optional, Dict, List

from config import DICTIONARY_API_BASE


MYMEMORY_API = "https://api.mymemory.translated.net/get"


async def fetch_chinese_translation(text: str) -> str:
    """Fetch Chinese translation via MyMemory API (free, no key needed)."""
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(
                MYMEMORY_API,
                params={"q": text, "langpair": "en|zh-CN"},
            )
            if resp.status_code == 200:
                data = resp.json()
                translated = data.get("responseData", {}).get("translatedText", "")
                if translated and translated.lower() != text.lower():
                    return translated
    except Exception:
        pass
    return ""


async def fetch_word_data(word: str) -> Optional[Dict]:
    """Fetch word data from Free Dictionary API.
    Returns parsed data with all meanings or None if not found.
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

        # extract all meanings across all parts of speech
        for m in entry.get("meanings", []):
            pos = m.get("partOfSpeech", "")
            for d in m.get("definitions", [])[:2]:  # max 2 per POS
                meaning = {
                    "partOfSpeech": pos,
                    "definition": d.get("definition", ""),
                    "example": d.get("example", ""),
                    "chinese": "",
                }
                result["meanings"].append(meaning)

        return result


async def translate_examples(meanings: List[Dict]) -> List[Dict]:
    """Translate the example sentences of each meaning to Chinese."""
    for m in meanings:
        if m.get("example") and not m.get("chinese"):
            cn = await fetch_chinese_translation(m["example"])
            if cn:
                m["chinese"] = cn
    return meanings
