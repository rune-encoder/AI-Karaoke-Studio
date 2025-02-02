# Standard Library Imports
import logging
import re

# Initialize Logger
logger = logging.getLogger(__name__)


def _condense_raw_lyrics(raw_lyrics):
    """
    Filters and formats raw lyrics data for processing.

    This function processes a list of verses, each containing word-level data,
    and extracts relevant information for each word. The extracted information
    includes the word itself, its start and end times, and its probability.

    Args:
        raw_lyrics (list): List of verses, where each verse is a dictionary
        containing a list of word dictionaries.

    Returns:
        list: A list of filtered and formatted word dictionaries.
    """
    filtered_words = []

    # Iterate over each verse in the raw lyrics
    for verse in raw_lyrics:

        # Iterate over each word in the verse
        for word in verse.get('words', []):

            # Ensure each word is a dictionary
            if isinstance(word, dict):  

                # Extract and format the word information
                filtered_word = {
                    'word': word.get('word', '').strip(),
                    'start': round(word.get('start', 0), 2),
                    'end': round(word.get('end', 0), 2),
                    # 'probability': round(word.get('probability', 0), 2),
                }

                # Add the formatted word to the filtered words list
                filtered_words.append(filtered_word)

    return filtered_words


def _clean_gemini_response(content):
    """
    Cleans the Gemini response by removing unwanted markdown formatting 
    and ensuring it contains valid JSON.

    This function performs the following steps:
    1. Removes markdown code block indicators (```json or ```) from the content.
    2. Extracts the first valid JSON object or array from the content.
    3. Cleans trailing commas within the JSON content to make it valid.
    4. Removes any additional leading or trailing whitespace from the cleaned content.

    Args:
        content (str): The raw content from Gemini, potentially containing 
                       markdown formatting or trailing characters.

    Returns:
        str: A cleaned JSON string.
    """
    # Step 1: Remove markdown code block indicators (```json or ```)
    if content.startswith("```json"):
        # Remove the ```json indicator and any surrounding ```
        content = content[7:].rstrip("```").strip()

    elif content.startswith("```"):
         # Remove the plain ``` indicator and any surrounding ```
        content = content[3:].rstrip("```").strip()  # Remove plain ```

    # Step 2: Extract the first valid JSON object or array
    # This ensures we only process the actual JSON data, ignoring trailing characters
    json_match = re.search(r"(\[.*\]|\{.*\})", content, re.DOTALL)

    if json_match:
         # Extract the JSON portion from the matched content
        content = json_match.group(1)

    # Step 3: Remove trailing commas within JSON objects/arrays
    # Use regex to remove trailing commas before closing brackets/braces
    content = re.sub(r",\s*([\]}])", r"\1", content)

    # Step 4: Remove any additional leading or trailing whitespace
    cleaned_content = content.strip()

    return cleaned_content


def _expand_gemini_lyrics(ai_output):
    """
    Converts AI-generated word alignments into a structured JSON format grouped by verses.
    Handles short verses and boundary overlaps explicitly.

    Args:
        ai_output (list): A list of WordAlignment objects, each with:
            - word (str): The word text.
            - start (float): The start time of the word.
            - end (float): The end time of the word.
            - verse_number (int): The verse number the word belongs to.

    Returns:
        list: A list of dictionaries, where each dictionary represents a verse.
    """

    # Step 1: Initialize the formatted output list
    formatted_output = []

    # Step 2: Group words by their `verse_number`
    grouped_verses = {}
    for word_alignment in ai_output:
        verse_number = word_alignment.verse_number

        # Initialize a new list for this verse if it doesn't already exist
        if verse_number not in grouped_verses:
            grouped_verses[verse_number] = []
        grouped_verses[verse_number].append(word_alignment)

    # Step 3: Process each verse
    for verse_number, words in sorted(grouped_verses.items()):
        # Get the start and end time of the verse
        verse_start = words[0].start  # Start time of the first word
        verse_end = words[-1].end    # End time of the last word

        # Build word details for the verse
        words_details = [
            {
                "word": word.word,
                "start": word.start,
                "end": word.end,
            }
            for word in words
        ]

        # Append the constructed verse to the formatted output
        formatted_output.append({
            "start": verse_start,
            "end": verse_end,
            "words": words_details,
        })

    return formatted_output