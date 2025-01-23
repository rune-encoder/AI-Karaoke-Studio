# Standard Library Imports
import logging
from pprint import pprint

# Local Application Imports
from .lyrics_cleaning import _condense_raw_lyrics, _expand_gemini_lyrics
from .lyrics_processor import _process_lyrics_in_chunks

# Initialize Logger
logger = logging.getLogger(__name__)

def _modify_lyrics_ai(raw_lyrics, reference_lyrics):
    """
    Modifies raw lyrics using AI by aligning them with official lyrics.

    This function condenses the raw lyrics, processes them in chunks, and formats
    the modified lyrics to match the official lyrics.

    Args:
        raw_lyrics (list): List of raw transcribed lyrics.
        reference_lyrics (list): List of official lyrics (verses as strings).

    Returns:
        list: Formatted and modified lyrics.
    """
    try:
        # Step 1: Condense raw lyrics into a simpler structure for processing
        compressed_raw_lyrics = _condense_raw_lyrics(raw_lyrics)
        logger.debug(f"Compressed raw lyrics for processing through AI")

        # Step 2: Flatten the list of verses into a list of words
        compressed_reference_lyrics = [
            word for verse in reference_lyrics for word in verse.split()
        ]
        logger.debug(f"Compressed official lyrics for processing through AI")

        # Step 3: Process the lyrics in chunks and align them
        modified_lyrics = _process_lyrics_in_chunks(compressed_raw_lyrics, compressed_reference_lyrics)
        logger.debug(f"Lyrics successfully processed through AI | {len(modified_lyrics)} words")

        print("ALIGNED LYRICS AFTER AI PROCESSING:")
        pprint(modified_lyrics, sort_dicts=False)

        # Step 4: Expand the processed lyrics back to the original verse structure
        formatted_modified_lyrics = _expand_gemini_lyrics(modified_lyrics, reference_lyrics)
        logger.debug(f"Lyrics format successfully expanded back to original structure")

        return formatted_modified_lyrics

    except Exception as e:
        logger.error(f"Error during lyrics modification: {e}")
        raise
