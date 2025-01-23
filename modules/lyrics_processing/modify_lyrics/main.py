from .lyrics_cleaning import _condense_raw_lyrics, _expand_gemini_lyrics
from .lyrics_processor import _process_lyrics_in_chunks
import logging

logger = logging.getLogger(__name__)

def _modify_lyrics_ai(raw_lyrics, official_lyrics):
    """
    Modifies raw lyrics using AI by aligning them with official lyrics.

    This function condenses the raw lyrics, processes them in chunks, and formats
    the modified lyrics to match the official lyrics.

    Args:
        raw_lyrics (list): List of raw transcribed lyrics.
        official_lyrics (list): List of official lyrics (verses as strings).

    Returns:
        list: Formatted and modified lyrics.
    """
    try:
        # Step 1: Condense raw lyrics into a simpler structure for processing
        compressed_raw_lyrics = _condense_raw_lyrics(raw_lyrics)

        # Step 2: Flatten the official lyrics into a list of words
        compressed_official_lyrics = [
            word for verse in official_lyrics for word in verse.split()
        ]

        # Step 3: Process the lyrics in chunks and align them
        modified_lyrics = _process_lyrics_in_chunks(
            compressed_raw_lyrics, compressed_official_lyrics, chunk_size=75
        )

        # Step 4: Expand the processed lyrics back to the original verse structure
        formatted_modified_lyrics = _expand_gemini_lyrics(modified_lyrics, official_lyrics)

        logger.info("Lyrics ai modification completed successfully!")
        return formatted_modified_lyrics

    except Exception as e:
        logger.error(f"Error during lyrics modification: {e}")
        raise
