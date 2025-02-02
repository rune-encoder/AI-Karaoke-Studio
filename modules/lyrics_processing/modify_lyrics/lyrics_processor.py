# Standard Library Imports
import logging
import json
import time
from pprint import pprint

# Third-Party Imports
from pydantic import ValidationError

# Local Application Imports
from .config import WordAlignmentList
from .gemini_setup import generate_prompt, llm
from .lyrics_cleaning import _clean_gemini_response

# Initialize Logger
logger = logging.getLogger(__name__)


def _chunk_lyrics(lyrics, chunk_size):
    """
    Splits a list of lyrics into smaller chunks of a specified size.

    Args:
        lyrics (list): A list of raw transcribed lyrics (e.g., words, phrases, or objects).
        chunk_size (int): The maximum number of items (e.g., words) in each chunk.

    Returns:
        list: A list of chunks, where each chunk is a list containing a subset of the lyrics.
    """
    try:
        # Confirm that the lyrics parameter is a list (of words, phrases, or objects)
        if not isinstance(lyrics, list):
            raise TypeError("The 'lyrics' parameter must be a list.")
        
        # Confirm that the chunk_size parameter is a positive integer
        if not isinstance(chunk_size, int) or chunk_size <= 0:
            raise ValueError("The 'chunk_size' parameter must be a positive integer.")

        # Generate chunks by slicing the lyrics list
        chunks = [lyrics[i:i + chunk_size] for i in range(0, len(lyrics), chunk_size)]
        logger.debug(f"Chunked lyrics into {len(chunks)} chunks, each with up to {chunk_size} words.")

        # Output => List[List[dict]]
        return chunks

    except Exception as e:
        logger.error(f"Error in _chunk_lyrics: {e}")
        raise


def _invoke_with_retries(prompt, max_retries=3, delay_between_retries=0.5):
    """
    Attempts to send a prompt to the LLM (Language Model) multiple times, 
    cleaning and validating the response after each attempt.

    Args:
        prompt (str): The generated prompt to send to the LLM.
        max_retries (int): The maximum number of retry attempts for obtaining a valid response.
        delay_between_retries (int): The time in seconds to wait between retries to avoid spamming the LLM.

    Returns:
        str: The cleaned and validated response content from the LLM.

    Raises:
        RuntimeError: If the maximum number of retries is exceeded without obtaining a valid response.
    """
    for attempt in range(1, max_retries + 1):
        try:
            # Attempt to invoke the LLM with the provided prompt
            logger.debug(f"Attempt {attempt}/{max_retries}: Sending prompt to the LLM.")
            response = llm.invoke(prompt)

            # Clean the response to ensure it is valid JSON
            cleaned_response = _clean_gemini_response(response.content)

            # Check if the cleaned response is valid (ends with "]" or "}")
            if cleaned_response.endswith("]") or cleaned_response.endswith("}"):
                logger.debug(f"Valid response obtained on attempt {attempt}.")
                return cleaned_response
            else:
                logger.warning(f"Incomplete JSON on attempt {attempt}, retrying...")

        # Log the exception that occurred during the attempt
        except Exception as e:
            logger.error(f"Error on attempt {attempt}: {e}")

        # Add a delay before the next retry (except after the last attempt)
        if attempt < max_retries:
            logger.debug(f"Waiting {delay_between_retries} seconds before retrying...")
            time.sleep(delay_between_retries)

    # Raise an error if all retry attempts fail
    raise RuntimeError(
        f"Failed to obtain a valid response after {max_retries} retries.")


def _validate_and_parse_response(cleaned_content):
    """
    Validates and parses the cleaned JSON response.

    This function ensures the JSON response conforms to the expected schema 
    (WordAlignmentList) and extracts the parsed WordAlignment objects.

    Args:
        cleaned_content (str): The cleaned JSON response from the LLM.

    Returns:
        List[WordAlignment]: A list of parsed WordAlignment objects.

    Raises:
        ValidationError: If the JSON does not conform to the expected schema.
        RuntimeError: If the JSON cannot be decoded.
    """
    try:
        # Attempt to validate and parse the JSON using the schema
        parsed_response = WordAlignmentList.model_validate_json(cleaned_content).root
        return parsed_response

    # Log detailed validation errors for debugging
    except ValidationError as ve:
        logger.error(f"Validation error while parsing response: {ve.json()}")
        raise ve

    # Handle generic JSON decoding errors
    except json.JSONDecodeError as je:
        logger.error(f"JSON decode error: {je}")
        raise RuntimeError("Failed to decode JSON response.") from je


def _process_lyrics_in_chunks(raw_lyrics, reference_lyrics, chunk_size=50):
    """
    Processes raw lyrics in chunks, aligning them with corrected lyrics.
    """
    # Split raw lyrics into smaller chunks: List[List[dict]]
    chunks = _chunk_lyrics(raw_lyrics, chunk_size)

    # Get the total number of chunks (each chunk is a list of word dictionaries)
    total_chunks = len(chunks)

    # Initialize a list to store the final aligned lyrics (list of WordAlignment objects)
    aligned_lyrics = []  

    # Initialize variables for tracking previous chunk's last word, verse, and time
    previous_chunk_last_word = None
    previous_chunk_last_verse = None
    previous_chunk_end_time = None

    # Initialize correction log
    correction_log = []

    # Iterate over each chunk in the cleaned "raw_lyrics" list and process it.
    for chunk_number, raw_chunk in enumerate(chunks, start=1):
        logger.info(f"Processing chunk {chunk_number}/{total_chunks}...")

        # Extract timing for the current chunk
        chunk_start_time = raw_chunk[0]['start']
        chunk_end_time = raw_chunk[-1]['end']

        # Determine the expected next word (if not the last chunk)
        expected_next_word = None
        if chunk_number < total_chunks:
            expected_next_word = chunks[chunk_number][0]['word']  # First word of next chunk

        # Generate the prompt for the current chunk
        prompt = generate_prompt(
            # Raw lyrics from transcription and reference lyrics for alignment
            raw_chunk,
            reference_lyrics,

            # Include batch information for tracking progress and context
            # Batch information: Chunk number, total chunks, and timing
            chunk_number,
            total_chunks,
            chunk_start_time,
            chunk_end_time,

            # Batch Information: Processed words, total words
            processed_words=len(aligned_lyrics),
            total_words=len(raw_lyrics),

            # Batch Information: Previous chunk context
            previous_chunk_last_word=previous_chunk_last_word,
            previous_chunk_last_verse=previous_chunk_last_verse,
            previous_chunk_end_time=previous_chunk_end_time,

            # Batch Information: Correction log and expected next word
            correction_log=correction_log,
            expected_next_word=expected_next_word
        )

        try:
            # Attempt to retrieve a cleaned response from the model
            cleaned_response = _invoke_with_retries(prompt)

            # Attempt to validate and parse the cleaned response from the model
            parsed_response = _validate_and_parse_response(cleaned_response)

            # Append processed lyrics to the result
            aligned_lyrics.extend(parsed_response)

            # Update previous chunk's last word, verse, and timing for the next iteration for prompt context
            if parsed_response:
                previous_chunk_last_word = parsed_response[-1].word
                previous_chunk_last_verse = parsed_response[-1].verse_number
                previous_chunk_end_time = parsed_response[-1].end

            # Update correction log with the latest corrections for prompt context
            for original, corrected in zip([word['word'] for word in raw_chunk], [word.word for word in parsed_response]):
                correction_log.append((original, corrected))

            logger.info(f"Successfully processed chunk {chunk_number}/{total_chunks}.")

        except Exception as e:
            logger.error(f"Error processing chunk {chunk_number}: {e}")
            raise e

    logger.info("Modified lyrics successfully processed in chunks!")

    return aligned_lyrics