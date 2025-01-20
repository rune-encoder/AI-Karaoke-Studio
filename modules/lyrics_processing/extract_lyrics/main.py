# Third-Party Imports
from faster_whisper import WhisperModel

# Local Application Imports
from .config import MODEL_SIZE, DEVICE, COMPUTE_TYPE

# Initialize Whisper model globally to avoid reloading it multiple times
MODEL = WhisperModel(MODEL_SIZE, device=DEVICE, compute_type=COMPUTE_TYPE)


def _extract_lyrics_with_timing(audio_path):
    """
    Extracts and groups lyrics into verses with timing and word details.

    Args:
        audio_path (str): Path to the audio file.

    Returns:
        list[dict]: List of verses with text and metadata.
    """
    # Transcribe the audio and extract word-level timestamps
    segments, info = MODEL.transcribe(audio_path, word_timestamps=True)

    # Initialize an empty list to hold the processed verses
    verses = []

    # Process each segment into a structured verse
    # Start indexing from 1
    for verse_index, segment in enumerate(segments, start=1):

        # Combine all words in the segment to form the full verse text
        verse_text = " ".join(word.word for word in segment.words)

        # Create metadata for each word in the segment
        words_metadata = []

        for word_index, word in enumerate(segment.words):
            word_data = {
                "word": word.word,
                "word_number": word_index + 1,  # Word index (1-based)
                "start": word.start,
                "end": word.end,
                "probability": word.probability  # Probability value
            }
            words_metadata.append(word_data)

        # Create the verse-level metadata dictionary
        verse_data = {
            "verse_number": verse_index,  # Verse index (1-based)
            "text": verse_text,           # Full text of the verse
            "start": segment.start,       # Start time of the verse
            "end": segment.end,           # End time of the verse
            "words": words_metadata       # Word-level metadata
        }

        # Append the verse metadata to the list of verses
        verses.append(verse_data)

    return verses
