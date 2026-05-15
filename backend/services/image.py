import httpx, random, hashlib, time
from typing import Optional, Tuple
from config import PEXELS_API_KEY, UNSPLASH_ACCESS_KEY

# PyInstaller bundled exe has SSL cert issues, disable verify for image APIs
_HTTPX_OPTS = {"verify": False}


def fetch_image_for_word(word: str, avoid_photo_id: Optional[str] = None) -> Tuple[Optional[str], str, Optional[str]]:
    """Fetch an image for the given word.
    Returns (image_url, source_name, photo_id) or (None, "", None).

    Strategy:
    1. Try Pexels API (free, 200 req/h)
    2. Fallback to Unsplash (free, 50 req/h)
    3. Fallback to Lorem Picsum (free, no API key, random photos)

    If avoid_photo_id is given, try to return a different photo.
    """
    url, source, photo_id = _try_pexels(word, avoid_photo_id)
    if url:
        return url, source, photo_id

    url, source, photo_id = _try_unsplash(word, avoid_photo_id)
    if url:
        return url, source, photo_id

    url, source, photo_id = _try_picsum(word, avoid_photo_id)
    if url:
        return url, source, photo_id

    return None, "", None


def _try_pexels(word: str, avoid_photo_id: Optional[str] = None) -> Tuple[Optional[str], str, Optional[str]]:
    if not PEXELS_API_KEY:
        return None, "", None
    try:
        resp = httpx.get(
            "https://api.pexels.com/v1/search",
            headers={"Authorization": PEXELS_API_KEY},
            params={"query": word, "per_page": 8, "orientation": "square"},
            timeout=10,
            **_HTTPX_OPTS,
        )
        if resp.status_code == 200:
            data = resp.json()
            photos = data.get("photos", [])
            if photos:
                # try to pick one that's different from the previous one
                candidates = [p for p in photos if str(p["id"]) != avoid_photo_id]
                if not candidates:
                    candidates = photos
                choice = random.choice(candidates)
                return choice["src"]["medium"], "pexels", str(choice["id"])
    except Exception:
        pass
    return None, "", None


def _try_unsplash(word: str, avoid_photo_id: Optional[str] = None) -> Tuple[Optional[str], str, Optional[str]]:
    if not UNSPLASH_ACCESS_KEY:
        return None, "", None
    try:
        resp = httpx.get(
            "https://api.unsplash.com/search/photos",
            headers={"Authorization": f"Client-ID {UNSPLASH_ACCESS_KEY}"},
            params={"query": word, "per_page": 8, "orientation": "squarish"},
            timeout=10,
            **_HTTPX_OPTS,
        )
        if resp.status_code == 200:
            data = resp.json()
            results = data.get("results", [])
            if results:
                candidates = [r for r in results if r["id"] != avoid_photo_id]
                if not candidates:
                    candidates = results
                choice = random.choice(candidates)
                return choice["urls"]["small"], "unsplash", choice["id"]
    except Exception:
        pass
    return None, "", None


def _try_picsum(word: str, avoid_photo_id: Optional[str] = None) -> Tuple[Optional[str], str, Optional[str]]:
    """Lorem Picsum — free image placeholder service, no API key needed."""
    import hashlib
    seed = word
    if avoid_photo_id:
        import time as _t
        seed = f"{word}-{int(_t.time())}"
    seed_hash = int(hashlib.md5(seed.encode()).hexdigest(), 16) % 1000000
    url = f"https://picsum.photos/seed/{seed_hash}/400/300"
    return url, "picsum", str(seed_hash)
