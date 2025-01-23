# Standard Library Imports
from pathlib import Path
from typing import Union
import logging

# Local Application Imports
from .main import _modify_lyrics_ai
from ...utilities import load_json, save_json

# Initialize Logger
logger = logging.getLogger(__name__)

def process_lyrics_modification(
    output_path: Union[str, Path],
    override: bool = False,
    file_name: str = "modified_ai_lyrics.json",
):
    """
    Processes and modifies lyrics using AI, saving the output to a file.

    This function checks for the existence of required input files (`official_lyrics.json`
    and `raw_lyrics.json`) and skips processing if the output file already exists
    unless the override flag is set.

    Args:
        output_path (Union[str, Path]): Directory to save the modified lyrics.
        override (bool): Whether to override the file if it already exists.
        file_name (str): Name of the output file to save the modified lyrics.

    Returns:
        str: Path to the saved modified lyrics file.
    """
    try:
        official_lyrics_file = Path(output_path) / "official_lyrics.json"
        raw_lyrics_file = Path(output_path) / "raw_lyrics.json"
        output_file = Path(output_path) / file_name

        # Step 1: Check if the output file already exists
        if output_file.exists() and not override:
            logger.info(
                f"Skipping lyrics modification... AI modified lyrics file already exists in the output directory."
            )
            return

        # Step 2: Ensure required input files exist
        if not official_lyrics_file.exists():
            logger.error(f"Official lyrics file does not exist. Skipping lyrics modification...")
            return

        if not raw_lyrics_file.exists():
            logger.error(f"Raw lyrics file does not exist. Skipping lyrics modification...")
            return

        # Step 3: Load the input files
        official_lyrics = load_json(official_lyrics_file)
        raw_lyrics = load_json(raw_lyrics_file)

        # Step 4: Modify the lyrics using the AI
        modified_lyrics = _modify_lyrics_ai(raw_lyrics, official_lyrics)

        # Step 5: Save the modified lyrics to the output file
        save_json(modified_lyrics, output_file)
        logger.info("Lyrics ai modification completed and saved successfully!")

        return

    except Exception as e:
        logger.error(f"Error during lyrics modification process: {e}")
        raise
