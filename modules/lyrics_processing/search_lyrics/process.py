from .main import _fetch_official_lyrics
import json
import logging
from pathlib import Path
from typing import Union
logger = logging.getLogger(__name__)


def process_lyric_search(
    output_path: Union[str, Path],
    override: bool = False,
    file_name: str = "official_lyrics.json",
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
    if output_file.exists() and not override or not metadata_file.exists():
        logger.info(
            "Skipping lyric search... Official lyrics file already exists in the output directory."
        )
        return

    try:
        with metadata_file.open("r", encoding="utf-8") as f:
            metadata = json.load(f)

        # Fetch official lyrics
        lyrics = _fetch_official_lyrics(metadata)

        # Save the lyrics as a JSON file
        with output_file.open("w", encoding="utf-8") as f:
            json.dump(lyrics, f, ensure_ascii=False, indent=4)

        logger.info("Official audio lyrics fetched and saved successfully!")

    except Exception as e:
        logger.error(f"Error processing lyric search: {e}")
        raise
