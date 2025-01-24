# Standard Library Imports
import logging
import re

# Third-Party Imports
import difflib

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
                    'word': word.get('word', '').strip().lower(),
                    'start': round(word.get('start', 0), 3),
                    'end': round(word.get('end', 0), 3),
                    'probability': round(word.get('probability', 0), 3),
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


def _expand_gemini_lyrics(ai_output, reference_lyrics):
    """
    Converts AI-generated word alignments into a structured JSON format aligned with cleaned lyrics.

    Args:
        ai_output (list): A list of WordAlignment objects, where each object contains:
            - word (str): The word from the AI output.
            - start (float): The start time of the word.
            - end (float): The end time of the word.
        reference_lyrics (list): A list of verses (strings) from the cleaned lyrics.
            Each verse is a line or group of words representing a segment of lyrics.

    Returns:
        list: A list of dictionaries representing formatted lyrics. Each dictionary includes:
            - verse_number (int): The sequential number of the verse.
            - text (str): The original text of the verse from reference_lyrics.
            - start (float): The start time of the first word in the verse.
            - end (float): The end time of the last word in the verse.
            - words (list): A list of word dictionaries, each containing:
                - word (str): The word text.
                - word_number (int): The position of the word in the verse.
                - start (float): The start time of the word.
                - end (float): The end time of the word.

    Raises:
        ValueError: If there is a mismatch in word alignment or if a verse cannot be fully aligned.

    Notes:
        - This function assumes `ai_output` is pre-sorted by time.
        - It logs warnings for any mismatches or leftover words but does not stop execution.
    """

    # Initialize the formatted output list
    formatted_output = []
    
    # Pointer to track the current position in the AI output
    word_index = 0  

    # Iterate through each verse in the cleaned lyrics
    for verse_number, verse_text in enumerate(reference_lyrics, start=1):
        verse_words = []        # List to store word-level details for this verse
        verse_start = None      # Start time of the verse
        verse_end = None        # End time of the verse

        # Split the verse text into individual words
        words_in_verse = verse_text.split()

        # Process each word in the current verse
        for word_number, word in enumerate(words_in_verse, start=1):
            
            # Check if we have exhausted the AI output
            if word_index >= len(ai_output):
                logger.warning(
                    f"Ran out of AI output while processing verse {verse_number}. "
                    f"Word: '{word}' (word {word_number} in verse)."
                )
                break

            # Retrieve the current word alignment from the AI output
            ai_word = ai_output[word_index]

            # Check if the words match (case-insensitive comparison)
            if ai_word.word != word.lower():
                logger.warning(
                    f"Mismatch detected in verse {verse_number}, word {word_number}: "
                    f"Expected '{word}', got '{ai_word.word}'."
                )

            # Set the start time of the verse if this is the first word
            if verse_start is None:
                verse_start = ai_word.start

            # Update the end time of the verse with the current word's end time
            verse_end = ai_word.end

            # Add word details to the verse
            verse_words.append({
                "word": ai_word.word,
                "word_number": word_number,
                "start": ai_word.start,
                "end": ai_word.end,
            })

            # Move to the next word in the AI output
            word_index += 1

        # Log if not all words in the verse could be aligned
        if len(verse_words) < len(words_in_verse):
            logger.warning(
                f"Not enough AI output words to fully align verse {verse_number}. "
                f"Expected {len(words_in_verse)}, got {len(verse_words)}."
            )

        # Append the verse details to the formatted output
        formatted_output.append({
            "verse_number": verse_number,
            "text": verse_text,
            "start": verse_start,
            "end": verse_end,
            "words": verse_words,
        })

    # Log any leftover words in the AI output
    if word_index < len(ai_output):
        logger.warning(
            f"Unused words in AI output. {len(ai_output) - word_index} words left unaligned."
        )

    return formatted_output