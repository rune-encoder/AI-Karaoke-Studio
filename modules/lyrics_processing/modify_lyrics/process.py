# Standard Library Imports
from pathlib import Path
from typing import Union
import logging

# Local Application Imports
from .main import _modify_lyrics_ai
from ...utilities import load_json, save_json

# Initialize Logger
logger = logging.getLogger(__name__)


def perform_lyric_enhancement(
    output_path: Union[str, Path],
    override: bool = False,
    file_name: str = "modified_lyrics.json",
):
    """
    Processes and modifies lyrics using AI, saving the output to a file.

    This function checks for the existence of required input files (`reference_lyrics.json`
    and `raw_lyrics.json`) and skips processing if the output file already exists
    unless the override flag is set.

    Args:
        output_path (Union[str, Path]): Directory to save the modified lyrics.
        override (bool): Whether to override the file if it already exists.
        file_name (str): Name of the output file to save the modified lyrics.
    """
    try:
        # Step 1: Check if the output file already exists
        output_file = Path(output_path) / file_name
        if output_file.exists() and not override:
            logger.info(
                f"Skipping lyrics modification... AI modified lyrics file already exists in the output directory."
            )
            return output_file

        # Step 2: Ensure required input files exist
        raw_lyrics_file = Path(output_path) / "raw_lyrics.json"
        if not raw_lyrics_file.exists():
            logger.warning(
                f"Raw lyrics file does not exist. Skipping lyrics modification...")
            return

        reference_lyrics_file = Path(output_path) / "reference_lyrics.json"
        if not reference_lyrics_file.exists():
            logger.warning(
                f"Official lyrics file does not exist. Skipping lyrics modification...")
            return

        # Step 3: Load the input files
        raw_lyrics = load_json(raw_lyrics_file)
        reference_lyrics = load_json(reference_lyrics_file)

        # Step 4: Modify the lyrics using the AI
        modified_lyrics = _modify_lyrics_ai(raw_lyrics, reference_lyrics)

        # Step 5: Save the modified lyrics to the output file
        save_json(modified_lyrics, output_file)
        logger.info("Lyrics ai modification completed and saved successfully!")
        return output_file

    except Exception as e:
        logger.error(f"Error during lyrics modification process: {e}")
        raise
