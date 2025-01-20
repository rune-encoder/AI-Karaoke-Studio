# Standard Library Imports
from pathlib import Path
from typing import Union
import logging
import json

# Local Application Imports
from .main import _extract_lyrics_with_timing
from ...utilities import ensure_file_exists

# Initialize Logger
logger = logging.getLogger(__name__)


def process_audio_extract_lyric_timing(
    output_path: Union[str, Path],
    override: bool = False,
    file_name: str = "raw_lyrics.json"
):
    # Check if the lyrics file already exists in the output directory and
    # skip the extraction if the override flag is not set
    output_file = Path(output_path) / file_name
    if output_file.exists() and not override:
        logger.info(
            "Skipping lyric extraction... Lyrics raw data already exist in the output directory...")
        return

    # Check if the vocals file exists. If not, raise an error.
    input_vocals = Path(output_path) / "vocals.mp3"
    ensure_file_exists(input_vocals, "Vocals file not found")

    try:
        # Extract lyrics metadata from the vocals stem
        lyrics_metadata = _extract_lyrics_with_timing(input_vocals)

        # Save lyrics raw metadata to a JSON file
        with open(output_file, "w") as f:
            json.dump(lyrics_metadata, f, indent=4)
        logger.info(f"Audio raw lyrics extracted successfully!")

    except Exception as e:
        logger.error(f"Erorr in extracting lyrics: {e}")
        raise RuntimeError(f"Erorr in extracting lyrics: {e}")
