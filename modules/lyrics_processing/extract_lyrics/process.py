# Standard Library Imports
from pathlib import Path
from typing import Union
import logging
import json

# Local Application Imports
from .main import _extract_lyrics_with_timing

# Initialize Logger
logger = logging.getLogger(__name__)


def transcribe_audio_lyrics(
    working_dir: Union[str, Path],
    override: bool = False,
    file_name: str = "raw_lyrics.json"
):
    # Check if the lyrics file already exists in the output directory and
    # skip the extraction if the override flag is not set
    output_file = Path(working_dir) / file_name
    if output_file.exists() and not override:
        logger.info(
            "Skipping lyric extraction... Lyrics raw data already exist in the output directory...")
        return output_file

    # Check if the vocals file exists. If not, raise an error.
    input_vocals = Path(working_dir) / "vocals.mp3"
    if not Path(input_vocals).exists():
        raise FileNotFoundError(f"Vocals file not found: {input_vocals}")

    try:
        logger.info("Transcribing raw lyrics from the vocals audio using Whisper model...")
        # Extract lyrics metadata from the vocals stem
        lyrics_metadata = _extract_lyrics_with_timing(input_vocals)

        # Save lyrics raw metadata to a JSON file
        with open(output_file, "w") as f:
            json.dump(lyrics_metadata, f, indent=4)
        logger.info(f"Transcribed vocals extracted successfully to: {output_file}")
        return output_file

    except Exception as e:
        raise RuntimeError(f"Error in extracting lyrics: {e}")
