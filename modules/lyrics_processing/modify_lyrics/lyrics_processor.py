# Standard Library Imports
import logging
import json
import time

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


def _invoke_with_retries(prompt, max_retries=3, delay_between_retries=1):
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

    # Iterate over each chunk in the "raw_lyrics" list and process it.
    for chunk_number, raw_chunk in enumerate(chunks, start=1):
        logger.info(f"Processing chunk {chunk_number}/{total_chunks}...")

        # Generate the prompt for the current chunk
        prompt = generate_prompt(raw_chunk, reference_lyrics, chunk_number, total_chunks)

        try:
            # Attempt to retrieve a cleaned response from the model
            cleaned_response = _invoke_with_retries(prompt)

            # Validate and parse the cleaned response
            parsed_response = _validate_and_parse_response(cleaned_response)

            # Append processed lyrics to the result
            aligned_lyrics.extend(parsed_response)

            # ! ================================================================
            # ! ================================================================
            # ! ================================================================

            # # Normalize both reference and parsed words
            # def normalize_text(text):
            #     return text.lower().strip().replace("'", "").replace('"', "")
            
            # # Check if the lengths match first
            # if len(reference_lyrics[:len(parsed_response)]) != len(parsed_response):
            #     logger.warning(
            #         f"Chunk {chunk_number}: Length mismatch! Reference length: "
            #         f"{len(reference_lyrics[:len(parsed_response)])}, Parsed length: {len(parsed_response)}"
            #     )
            # else:
            #     # Normalize and compare content directly
            #     def normalize_text(text):
            #         return text.lower().strip().replace("'", "").replace('"', "")

            #     # Normalize both reference and parsed words
            #     normalized_reference = [normalize_text(word) for word in reference_lyrics[:len(parsed_response)]]
            #     normalized_parsed = [normalize_text(word_alignment.word) for word_alignment in parsed_response]

            #     if normalized_reference != normalized_parsed:
            #         logger.warning(f"Mismatch in chunk {chunk_number}: Content mismatch!")
            #         for i, (ref_word, parsed_word) in enumerate(zip(normalized_reference, normalized_parsed)):
            #             if ref_word != parsed_word:
            #                 logger.debug(f"Mismatch at position {i}: Reference '{ref_word}' vs Parsed '{parsed_word}'")

            # Check if the parsed response length matches the chunk length
            # logger.debug(f"Chunk {chunk_number} | Reference {reference_lyrics[:len(parsed_response)]} | Parsed {parsed_response}")
            # if reference_lyrics[:len(parsed_response)] != parsed_response:
            #     logger.warning("Mismatch between parsed response and reference lyrics.")

            # ! ================================================================
            # ! ================================================================
            # ! ================================================================
            
            # Update the corrected_lyrics to remove matched words
            reference_lyrics = reference_lyrics[len(parsed_response):]
            logger.info(f"Successfully processed chunk {chunk_number}/{total_chunks}.")

        except Exception as e:
            logger.error(f"Error processing chunk {chunk_number}: {e}")
            raise e

    logger.info("Modified lyrics successfully processed in chunks!")
    return aligned_lyrics