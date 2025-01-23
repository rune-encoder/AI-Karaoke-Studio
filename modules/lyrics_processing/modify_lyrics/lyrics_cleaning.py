# Standard Library Imports
import re
from pprint import pprint

def _condense_raw_lyrics(raw_lyrics):
    """
    Filters and formats raw lyrics data for processing.

    Args:
        raw_lyrics (list): List of verses containing word-level data.

    Returns:
        list: A list of filtered and formatted word dictionaries.
    """
    filtered_words = []

    for verse in raw_lyrics:
        for word in verse.get('words', []):
            if isinstance(word, dict):  # Ensure each word is a dictionary
                filtered_word = {
                    'word': word.get('word', '').strip().lower(),
                    'start': round(word.get('start', 0), 3),
                    'end': round(word.get('end', 0), 3),
                    'probability': round(word.get('probability', 0), 3),
                }
                filtered_words.append(filtered_word)

    pprint(filtered_words, sort_dicts=False)
    return filtered_words


def _clean_gemini_response(content):
    """
    Cleans the Gemini response by removing unwanted markdown formatting 
    and ensuring it contains valid JSON.

    Args:
        content (str): The raw content from Gemini, potentially containing 
                       markdown formatting or trailing characters.

    Returns:
        str: A cleaned JSON string.
    """
    # Step 1: Remove markdown code block indicators (```json or ```)
    if content.startswith("```json"):
        content = content[7:].rstrip("```").strip()  # Remove ```json and surrounding ```
    elif content.startswith("```"):
        content = content[3:].rstrip("```").strip()  # Remove plain ```

    # Step 2: Extract the first valid JSON object or array
    # This ensures we only process the actual JSON data, ignoring trailing characters
    json_match = re.search(r"(\[.*\]|\{.*\})", content, re.DOTALL)
    if json_match:
        content = json_match.group(1)  # Extract the JSON portion

    # Step 3: Remove any additional leading or trailing whitespace
    cleaned_content = content.strip()

    return cleaned_content


def _expand_gemini_lyrics(ai_output, cleaned_lyrics):
    """
    Formats the AI output into the desired JSON structure based on cleaned_lyrics.

    Args:
        ai_output (list): List of WordAlignment objects.
        cleaned_lyrics (list): List of verses (strings with more than one word).

    Returns:
        list: Formatted lyrics in the desired JSON structure.
    """
    formatted_output = []
    word_index = 0  # Pointer to iterate over ai_output

    for verse_number, verse_text in enumerate(cleaned_lyrics, start=1):
        verse_words = []  # List to store words for this verse
        verse_start = None
        verse_end = None

        # Split the verse into individual words for alignment
        words_in_verse = verse_text.split()

        for word_number, word in enumerate(words_in_verse, start=1):
            # Match the next word from the AI output
            if word_index < len(ai_output):
                ai_word = ai_output[word_index]
                if verse_start is None:
                    verse_start = ai_word.start  # Set the start time of the verse
                verse_end = ai_word.end  # Update the end time of the verse

                # Add the word details to this verse
                verse_words.append({
                    "word": ai_word.word,
                    "word_number": word_number,
                    "start": ai_word.start,
                    "end": ai_word.end,
                })

                word_index += 1  # Move to the next AI output word

        # Construct the verse object
        formatted_output.append({
            "verse_number": verse_number,
            "text": verse_text,
            "start": verse_start,
            "end": verse_end,
            "words": verse_words,
        })

    return formatted_output
