# Standard Imports
from pathlib import Path
from typing import Union
import logging

# Third-Party Imports
from faster_whisper import WhisperModel

# Local Application Imports
from .config import MODEL_SIZE, DEVICE, COMPUTE_TYPE
from interface.helpers import get_available_languages

# Initialize Whisper model globally to avoid reloading it multiple times
MODEL = WhisperModel(MODEL_SIZE, device=DEVICE, compute_type=COMPUTE_TYPE)

# Initialize Logger
logger = logging.getLogger(__name__)

def _extract_lyrics_with_timing(
        audio_path: Union[str, Path],
        beam_size_input: int = 15,
        best_of_input: int = 5,
        patience_input: float = 3.0,
        condition_toggle: bool = False,
        compression_threshold_input: float = 1.3,
        temperature_input: float = 0.0,
        language_option: str = "Auto Detect"
    ):
    """
    Extracts and groups lyrics into verses with timing and word details.

    Args:
        audio_path (str): Path to the audio file.

    Returns:
        list[dict]: List of verses with text and metadata.
    """
    # If the user chooses Auto Detect, we let Whisper decide (or pass None)
    if language_option == "Auto Detect":
        lang = None
    else:
        available_langs = get_available_languages()
        lang = available_langs.get(language_option, None)

    # Transcribe the audio and extract word-level timestamps
    segments, info = MODEL.transcribe(
        audio_path,
        word_timestamps=True,              # Extract word-level timestamps
        beam_size=int(beam_size_input),    # Increase beam search for better word accuracy
        best_of=int(best_of_input),        # Pick the best transcription from multiple runs
        patience=patience_input,           # Allow more time before closing segments
        condition_on_previous_text=condition_toggle,             # Ensure no contextual bias from previous words
        compression_ratio_threshold=compression_threshold_input, # Force Whisper to retain more words
        temperature=temperature_input,       # Eliminate randomness in transcription
        language=lang                       # Language code for transcription
    )

    logger.debug(f"Transcription of the vocals audio segments completed.")
    print("INFO:", info)

    # Initialize an empty list to hold the processed verses
    verses = []

    # Process each segment into a structured verse
    logger.debug(f"Formatting segments into verses with words, timing, and predictions using the Whisper model.")
    for segment in segments:

        # Create metadata for each word in the segment
        words_metadata = []

        for word in segment.words:
            word_data = {
                "word": word.word.strip(),
                "start": round(word.start, 2),
                "end": round(word.end, 2),
                "probability": round(word.probability, 2)   # Probability value
            }
            words_metadata.append(word_data)

        # Create the verse-level metadata dictionary
        verse_data = {
            "start": round(segment.start, 2),       # Start time of the verse
            "end": round(segment.end, 2),           # End time of the verse
            "words": words_metadata       # Word-level metadata
        }

        # Append the verse metadata to the list of verses
        verses.append(verse_data)

    logger.debug(f"Transcribed {len(verses)} verses with words, timing, and predictions using the Whisper model.")
    return verses
