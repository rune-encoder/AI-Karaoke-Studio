# Standard Library Imports
import logging
from pprint import pprint

# Local Application Imports
from .lyrics_cleaning import _condense_raw_lyrics, _expand_gemini_lyrics
from .lyrics_processor import _process_lyrics_in_chunks

# Initialize Logger
logger = logging.getLogger(__name__)

# ! Temporary fix for verse alignment => Capitalization detection
# ! ============================================================================
def _ensure_consistent_verse_boundaries(ai_output):
    """
    Ensures each verse has consistent capitalization and boundary alignment.

    Args:
        ai_output (list): List of WordAlignment objects with updated verse assignments.

    Returns:
        list: Verified and corrected list of WordAlignment objects.
    """
    for i, word_alignment in enumerate(ai_output):
        # Check if the current word is lowercase and incorrectly starts a verse
        if word_alignment.word[0].islower():
            # Look backward for the previous word in the same verse
            for j in range(i - 1, -1, -1):
                if ai_output[j].verse_number == word_alignment.verse_number:
                    # If previous word starts with uppercase, adjust the current word
                    if ai_output[j].word[0].isupper():
                        word_alignment.verse_number = ai_output[j].verse_number
                        break
                else:
                    break
    return ai_output
# ! ============================================================================

# ! Temporary fix for verse alignment => Capitalization detection
# ! ============================================================================
def _fix_verse_assignment_with_capitalization(ai_output):
    """
    Adjusts verse assignments by detecting capitalized words and fixing spillage.

    Args:
        ai_output (list): List of WordAlignment objects with initial verse assignments.

    Returns:
        list: Updated list of WordAlignment objects with corrected verse numbers.
    """
    # Helper variable to track the start of the current verse
    current_verse_start = 0

    for i, word_alignment in enumerate(ai_output):
        # Ignore single-character "I" as it's not a verse boundary
        if word_alignment.word == "I":
            continue

        # Capitalization and punctuation-based verse boundary detection
        is_new_verse = (
            word_alignment.word[0].isupper() or  # Starts with uppercase
            (i > 0 and ai_output[i - 1].word[-1] in "?!.")  # Follows punctuation
        )

        if is_new_verse:
            # Adjust previous words in the same verse
            for j in range(i - 1, current_verse_start - 1, -1):
                # Stop backtracking if the verse number changes
                if ai_output[j].verse_number != word_alignment.verse_number:
                    break
                # Reassign to the previous verse
                ai_output[j].verse_number -= 1

            # Update the start of the current verse
            current_verse_start = i

    # Post-process to ensure all verses have consistent boundaries
    ai_output = _ensure_consistent_verse_boundaries(ai_output)
    return ai_output
# ! ============================================================================


def _modify_lyrics_ai(raw_lyrics, reference_lyrics):
    """
    Modifies raw lyrics using AI by aligning them with official lyrics.

    This function condenses the raw lyrics, processes them in chunks, and formats
    the modified lyrics to match the official lyrics.

    Args:
        raw_lyrics (list): List of raw transcribed lyrics.
        reference_lyrics (list): List of official lyrics (verses as strings).

    Returns:
        list: Formatted and modified lyrics.
    """
    try:
        # Step 1: Condense raw lyrics into a simpler structure for processing
        compressed_raw_lyrics = _condense_raw_lyrics(raw_lyrics)
        logger.debug(f"Compressed raw lyrics for processing through AI | {len(compressed_raw_lyrics)} words")

        # Step 2: Flatten reference lyrics into (word, verse_number) tuples
        compressed_reference_lyrics = [
            (word, verse_number)
            for verse_number, verse in enumerate(reference_lyrics, start=1)
            for word in verse.split()
        ]
        logger.debug(f"Compressed official lyrics for processing through AI | {len(compressed_reference_lyrics)} words")

        # Step 3: Process the lyrics in chunks and align them
        modified_lyrics = _process_lyrics_in_chunks(compressed_raw_lyrics, compressed_reference_lyrics)
        logger.debug(f"Lyrics successfully processed through AI | {len(modified_lyrics)} words")

        # ! Save aligned lyrics for debugging
        import pickle
        with open('aligned_lyrics.pkl', 'wb') as f:
            pickle.dump(modified_lyrics, f)

        # ! Temporary fix for verse alignment => Capitalization detection 
        # ! ====================================================================
        # modified_lyrics = _fix_verse_assignment_with_capitalization(modified_lyrics)
        # print("ALIGNED LYRICS AFTER AI PROCESSING:")
        # pprint(modified_lyrics, sort_dicts=False)
        # ! ====================================================================

        # Step 4: Expand the processed lyrics back to the original verse structure
        formatted_modified_lyrics = _expand_gemini_lyrics(modified_lyrics)
        logger.debug(f"Lyrics format successfully expanded back to original structure")

        return formatted_modified_lyrics

    except Exception as e:
        logger.error(f"Error during lyrics modification: {e}")
        raise
