import os
import asyncio
from config import AUDIO_DIR


def generate_audio_for_word(word: str) -> str:
    """Generate American English audio for a word using edge-tts.
    Returns the file path to the generated audio.
    """
    safe_name = word.lower().replace(" ", "_").replace("'", "_")
    file_path = os.path.join(AUDIO_DIR, f"{safe_name}.mp3")

    if os.path.exists(file_path):
        return file_path

    try:
        import edge_tts
        text = word.replace("-", " ")
        # Use en-US voice for American pronunciation
        asyncio.run(
            edge_tts.Communicate(text, voice="en-US-JennyNeural").save(file_path)
        )
        return file_path
    except Exception as e:
        raise RuntimeError(f"Failed to generate audio for '{word}': {e}")
