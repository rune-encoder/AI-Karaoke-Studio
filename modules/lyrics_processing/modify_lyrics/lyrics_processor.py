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
    # Validate inputs
    if not isinstance(lyrics, list):
        raise TypeError("The 'lyrics' parameter must be a list.")

    if not isinstance(chunk_size, int) or chunk_size <= 0:
        raise ValueError(
            "The 'chunk_size' parameter must be a positive integer.")

    # Generate chunks by slicing the lyrics list
    chunks = [lyrics[i:i + chunk_size]
              for i in range(0, len(lyrics), chunk_size)]

    return chunks


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
            response = llm.invoke(prompt)

            # Clean the response to ensure valid JSON
            cleaned_content = _clean_gemini_response(response.content)

            # Check if the cleaned response is valid (ends with "]" or "}")
            if cleaned_content.endswith("]") or cleaned_content.endswith("}"):
                print(f"[Retry Attempt {attempt}] Valid Response Obtained.")
                return cleaned_content
            else:
                print(
                    f"[Retry Attempt {attempt}] Incomplete JSON, retrying...")

        except Exception as e:
            # Log the exception during the attempt
            print(f"[Retry Attempt {attempt}] Failed with error: {e}")

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
        print("[ERROR] Validation Error while parsing response:")
        print(ve.json())  # Outputs detailed error messages in JSON format
        raise ve

    except json.JSONDecodeError as je:
        # Handle generic JSON decoding errors
        print("[ERROR] JSON Decode Error while parsing response:")
        print(str(je))
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

    for chunk_number, raw_chunk in enumerate(chunks, start=1):
        print(f"\n--- Processing Chunk {chunk_number}/{total_chunks} ---")

        # Debug: Display the current chunk and corresponding corrected lyrics
        print(
            f"[INFO] Corrected Lyrics for Current Chunk: {chunk_number}/{total_chunks}")
        pprint(corrected_lyrics, sort_dicts=False)

        print(
            f"[INFO] Raw Lyrics for Current Chunk: {chunk_number}/{total_chunks}")
        pprint(raw_chunk, sort_dicts=False)

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
                print("[ERROR] Validation Error Details:")
                print(ve.json())  # Debugging validation errors
                raise ve

            # Debug: Display parsed response for the current chunk
            print("[INFO] Parsed Response for Current Chunk:")
            pprint(parsed_response)

            # Append processed lyrics to the result and update the corrected lyrics
            aligned_lyrics.extend(parsed_response)
            corrected_lyrics = corrected_lyrics[len(parsed_response):]

        except Exception as e:
            print(
                f"[ERROR] An error occurred while processing chunk {chunk_number}/{total_chunks}: {e}")
            raise e

    # Return the combined list of aligned lyrics
    return aligned_lyrics
