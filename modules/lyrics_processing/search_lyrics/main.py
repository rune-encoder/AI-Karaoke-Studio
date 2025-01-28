# Standard Library Imports
import logging
import re

# Local Application Imports
from .config import GENIUS_API_TOKEN
from .utilities import (
    _search_genius_lyrics,
    _scrape_genius_lyrics,
    _clean_genius_lyrics,
)

# Initialize Logger
logger = logging.getLogger(__name__)


def _fetch_official_lyrics(metadata):
    """
    Fetch and clean official lyrics from Genius using song metadata.

    Args:
        metadata (dict): Dictionary containing song metadata with keys:
                         - title: Title of the song
                         - artists: Artist name

    Returns:
        list: Cleaned lyrics as a list of verses (strings).

    Raises:
        ValueError: If the song cannot be found or lyrics are unavailable.
    """
    # Remove any text within parentheses from the title
    title = re.sub(r"\(.*?\)", "", metadata["title"]).strip()

    # Join multiple artists into a single string
    artist = ", ".join(metadata["artists"]) if isinstance(metadata["artists"], list) else metadata["artists"]

    try:
        # Search for the song on Genius
        logger.debug(f"Searching for lyrics on Genius for '{title}' by '{artist}'...")
        url = _search_genius_lyrics(title, artist, api_key=GENIUS_API_TOKEN)

        if not url:
            logger.error(f"No lyrics found for '{title}' by '{artist}'.")
            raise ValueError(f"No lyrics found for '{title}' by '{artist}'.") 
        else:
            logger.debug(f"Lyrics found at URL: {url}")

        # Scrape lyrics from the Genius page
        lyrics = _scrape_genius_lyrics(url)
        if not lyrics:
            logger.error(f"Lyrics could not be scraped for '{title}' by '{artist}'.")
            raise ValueError(f"Lyrics could not be scraped for '{title}' by '{artist}'.") 

        # Clean the scraped lyrics
        cleaned_lyrics = _clean_genius_lyrics(lyrics)
        return cleaned_lyrics

    except Exception as e:
        logger.error(f"Error fetching lyrics: {e}")
        raise RuntimeError(f"Error fetching lyrics: {e}")
