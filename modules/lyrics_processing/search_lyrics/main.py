# Standard Library Imports
import logging

# Local Application Imports
from .utilities import (
    _search_genius_lyrics,
    _scrape_genius_lyrics,
    _clean_genius_lyrics,
)
from .config import GENIUS_API_TOKEN

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

    title = metadata["title"]
    artist = metadata["artists"]

    try:
        # Search for the song on Genius
        logger.debug(f"Searching for lyrics on Genius for '{title}' by '{artist}'...")
        url = _search_genius_lyrics(title, artist, api_key=GENIUS_API_TOKEN)

        if not url:
            logger.warning(f"No lyrics found for '{title}' by '{artist}'.")
            return False
        else:
            logger.debug(f"Lyrics found at URL: {url}")

        # Scrape lyrics from the Genius page
        lyrics = _scrape_genius_lyrics(url)
        if not lyrics:
            logger.warning(f"Lyrics could not be scraped for '{title}' by '{artist}'.")
            return False

        # Clean the scraped lyrics
        cleaned_lyrics = _clean_genius_lyrics(lyrics)

        return cleaned_lyrics

    except Exception as e:
        logger.error(f"Error fetching lyrics: {e}")
        raise
