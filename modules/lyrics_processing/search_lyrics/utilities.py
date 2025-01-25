# Standard Library Imports
from bs4 import BeautifulSoup
import logging
import requests
import re

# Local Application Imports
from .config import GENIUS_API_TOKEN

# Initialize Logger
logger = logging.getLogger(__name__)


def _search_genius_lyrics(title, artist, api_key=GENIUS_API_TOKEN):
    """
    Search the Genius API for a song by title and artist.

    Args:
        title (str): The title of the song to search.
        artist (str): The artist of the song to search.
        api_key (str): The Genius API key for authentication.

    Returns:
        dict or None: The first result from the Genius API search, or None if no results are found.

    Raises:
        Exception: If the API request fails or returns an error response.
    """

    # API endpoint and headers
    base_url = "https://api.genius.com/search"
    headers = {"Authorization": f"Bearer {api_key}"}
    params = {"q": f"{title} {artist}"}

    # Make the API request
    response = requests.get(base_url, headers=headers, params=params)

    # Check for errors in the response status code
    if response.status_code != 200:
        raise Exception(
            f"Genius API error: {response.status_code}, {response.json()}"
        )

    # Parse the JSON response
    data = response.json()
    hits = data.get("response", {}).get("hits", [])

    if not hits:
        return None

    # Validate the results returned by the Genius API
    for hit in hits:  # Iterate through each search result (hit) from the API response

        # Extract and normalize the song title and artist name from the current hit
        result_title = hit["result"]["title"].lower()  # Convert the song title to lowercase for case-insensitive comparison
        result_artist = hit["result"]["primary_artist"]["name"].lower()  # Convert the artist name to lowercase for case-insensitive comparison

        # Check if the input title and artist match the current result
        # - 'title.lower() in result_title' ensures the desired title is part of the result's title
        # - 'artist.lower() in result_artist' ensures the desired artist is part of the result's artist name
        if title.lower() in result_title and artist.lower() in result_artist:
            # If both title and artist match, return the URL of the matching result
            logger.debug(f"Exact match found for '{title}' by '{artist}'.")
            return hit["result"]["url"]
    
    # If no matching results are found, the function will return the first result URL
    logger.debug(f"No exact match found for '{title}' by '{artist}'. Returning the first result URL.")
    return hits[0]["result"]["url"]


def _scrape_genius_lyrics(url):
    """
    Scrape lyrics from a Genius song URL.

    Args:
        url (str): The URL of the Genius song page to scrape.

    Returns:
        list[str]: A list of lyric lines extracted from the page.

    Raises:
        Exception: If the page request fails or no lyrics are found.
    """
    # Fetch the Genius song page
    response = requests.get(url)
    if response.status_code != 200:
        raise Exception(f"Failed to fetch Genius page: {response.status_code}")

    # Parse the page content using BeautifulSoup
    soup = BeautifulSoup(response.text, "html.parser")

    # Find all divs with the attribute 'data-lyrics-container'
    lyrics_containers = soup.find_all(
        "div", attrs={"data-lyrics-container": "true"})

    if not lyrics_containers:
        raise Exception("No lyrics containers found on the page.")

    # Extract and clean the text from the containers
    lyrics = []
    for container in lyrics_containers:
        for line in container.stripped_strings:
            lyrics.append(line)

    return lyrics


def _clean_genius_lyrics(fetched_lyrics):
    """
    Preprocess Genius lyrics by cleaning metadata, removing Unicode spaces, 
    and splitting into individual lines.

    Args:
        fetched_lyrics (list[str]): Raw list of lyric lines from Genius.

    Returns:
        list[str]: A cleaned and processed list of lyric lines.
    """
    # Combine the fetched lyrics into a single string for processing
    lyrics_text = "\n".join(fetched_lyrics)

    # Remove metadata like [Verse 1], [Chorus], etc.
    lyrics_text = re.sub(r"\[.*?\]", "", lyrics_text)

    # Replace unusual Unicode spaces with regular spaces
    lyrics_text = re.sub(r"[\u2000-\u200A]", " ", lyrics_text)

    # Split into individual lines and remove empty lines
    cleaned_lyrics = [line.strip() for line in lyrics_text.split("\n") if line.strip()]

    return cleaned_lyrics
