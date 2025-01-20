import json
import logging
from pathlib import Path
from typing import Union

from .main import _extract_lyrics_with_timing

from ...utilities import ensure_file_exists

logging.basicConfig(level=logging.INFO)

def process_audio_extract_lyric_timing(
    output_path: Union[str, Path],
    override: bool = False,
    file_name: str = "raw_lyrics.json"
):
    """
    Extract lyrics with timing metadata from an audio file.

    Args:
        input_file (str): Path to the vocals stem audio file.

    Returns:
        str: Path to the saved raw lyrics metadata JSON file.
    """

    output_file = Path(output_path) / file_name
    if output_file.exists() and not override:
        logging.info("Lyrics already extracted. Skipping...")
        return

    input_vocals = Path(output_path) / "vocals.mp3"
    ensure_file_exists(input_vocals, "Vocals file not found")

    try:
        # Extract lyrics metadata
        lyrics_metadata = _extract_lyrics_with_timing(input_vocals)

        # Save raw metadata to JSON
        with open(output_file, "w") as f:
            json.dump(lyrics_metadata, f, indent=4)
        logging.info(f"Lyrics saved to {output_file}")

    except Exception as e:
        logging.error(f"An error occurred during lyric extraction: {e}")