# Standard Library Imports
from pathlib import Path
from typing import Union
import logging

# Local Application Imports
from .main import _fetch_official_lyrics
from ...utilities import load_json, save_json

# Initialize Logger
logger = logging.getLogger(__name__)

def fetch_and_save_lyrics(
    output_path: Union[str, Path],
    override: bool = False,
    file_name: str = "reference_lyrics.json",
):
    """
    Process the lyric search and save the fetched lyrics to a file.

    Args:
        output_path (Union[str, Path]): Directory to save the fetched lyrics.
        override (bool): Whether to override the file if it already exists.
        file_name (str): Name of the output file to save the lyrics.
    """
    metadata_file = Path(output_path) / "metadata.json"

    # Check if the file already exists in the output directory and
    # skip the search if the override flag is not set
    output_file = Path(output_path) / file_name
    if output_file.exists() and not override:
        logger.info(
            "Skipping lyric search... Official lyrics file already exists in the output directory."
        )
        return
    
    if not metadata_file.exists():
        logger.error("Metadata file does not exist. Skipping lyric search...")
        raise FileNotFoundError("Metadata file does not exist.")

    try:
        logger.info("Fetching official audio lyrics to reference for AI modification...")
        
        # Load the audio metadata file
        metadata = load_json(metadata_file)

        # Fetch official lyrics
        lyrics = _fetch_official_lyrics(metadata)

        # Save the lyrics as a JSON file
        save_json(lyrics, output_file)

        logger.info("Official audio lyrics fetched and saved successfully!")

    except Exception as e:
        logger.error(f"Error processing lyric search: {e}")
        raise RuntimeError(f"Error processing lyric search: {e}")
