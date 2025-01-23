# Standard Library Imports
import logging
from pprint import pprint
import json

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
        # Validate inputs
        if not isinstance(lyrics, list):
            raise TypeError("The 'lyrics' parameter must be a list.")

        if not isinstance(chunk_size, int) or chunk_size <= 0:
            raise ValueError("The 'chunk_size' parameter must be a positive integer.")

        # Generate chunks by slicing the lyrics list
        chunks = [lyrics[i:i + chunk_size] for i in range(0, len(lyrics), chunk_size)]

        logger.debug(f"Chunked lyrics into {len(chunks)} chunks of size {chunk_size}.")
        return chunks

    except Exception as e:
        logger.error(f"Error in _chunk_lyrics: {e}")
        raise


def _retry_with_chunks(prompt, max_retries=3):
    """
    Attempts to send a prompt to the LLM (Language Model) multiple times, 
    cleaning and validating the response after each attempt.

    Args:
        prompt (str): The generated prompt to send to the LLM.
        max_retries (int): The maximum number of retry attempts for obtaining a valid response.

    Returns:
        str: The cleaned and validated response content from the LLM.

    Raises:
        RuntimeError: If the maximum number of retries is exceeded without obtaining a valid response.
    """
    for attempt in range(1, max_retries + 1):
        try:
            # Invoke the LLM with the provided prompt
            logger.debug(f"Attempt {attempt}/{max_retries}: Sending prompt to the LLM.")
            response = llm.invoke(prompt)

            # Clean the response to ensure valid JSON
            cleaned_content = _clean_gemini_response(response.content)

            # Check if the cleaned response is valid (ends with "]" or "}")
            if cleaned_content.endswith("]") or cleaned_content.endswith("}"):
                logger.debug(f"Valid response obtained on attempt {attempt}.")
                return cleaned_content
            else:
                logger.warning(f"Incomplete JSON on attempt {attempt}, retrying...")

        except Exception as e:
            # Log the exception during the attempt
            logger.error(f"Error on attempt {attempt}: {e}")

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
        parsed_response = WordAlignmentList.model_validate_json(
            cleaned_content).root
        return parsed_response

    except ValidationError as ve:
        # Log detailed validation errors for debugging
        logger.error(f"Validation error while parsing response: {ve.json()}")
        raise ve

    except json.JSONDecodeError as je:
        # Handle generic JSON decoding errors
        logger.error(f"JSON decode error: {je}")
        raise RuntimeError("Failed to decode JSON response.") from je


def _process_lyrics_in_chunks(raw_lyrics, corrected_lyrics, chunk_size=50):
    """
    Processes raw lyrics in chunks, aligning them with corrected lyrics.

    This function splits the raw lyrics into smaller chunks, processes each chunk using
    a language model, and aligns the transcriptions with the corrected lyrics.

    Args:
        raw_lyrics (list): The raw transcribed lyrics.
        corrected_lyrics (list): The corrected lyrics.
        chunk_size (int): Number of words per chunk.

    Returns:
        list: A combined response of aligned lyrics from all chunks.

    Raises:
        Exception: If an error occurs while processing any chunk.
    """
    # Split raw lyrics into smaller chunks
    chunks = _chunk_lyrics(raw_lyrics, chunk_size)
    total_chunks = len(chunks)
    aligned_lyrics = []  # To store the final aligned lyrics

    logger.info(f"Processing {total_chunks} chunks of raw lyrics.")
    for chunk_number, raw_chunk in enumerate(chunks, start=1):
        logger.info(f"Processing chunk {chunk_number}/{total_chunks}...")

        # Debug: Log the chunk and corresponding corrected lyrics
        logger.debug(f"Raw Chunk {chunk_number}: {raw_chunk}")
        logger.debug(f"Corrected Lyrics: {corrected_lyrics}")

        # Generate the prompt for the current chunk
        prompt = generate_prompt(
            raw_chunk, corrected_lyrics, chunk_number, total_chunks)

        try:
            # Attempt to retrieve a cleaned response from the model
            cleaned_content = _retry_with_chunks(prompt)

            # Validate and parse the cleaned response
            try:
                parsed_response = _validate_and_parse_response(cleaned_content)

            except ValidationError as ve:
                logger.error(f"Validation error while processing chunk {chunk_number}/{total_chunks}: {ve.json()}")
                raise ve

            # Append processed lyrics to the result and update the corrected lyrics
            aligned_lyrics.extend(parsed_response)
            corrected_lyrics = corrected_lyrics[len(parsed_response):]

            logger.info(f"Successfully processed chunk {chunk_number}/{total_chunks}.")

        except Exception as e:
            logger.error(f"Error processing chunk {chunk_number}: {e}")
            raise e

    # Return the combined list of aligned lyrics
    logger.info("All chunks processed successfully.")
    return aligned_lyrics
