# Standard Library Imports
from pathlib import Path
from typing import Union
import logging

# Local Application Imports
from modules import (
    initialize_working_directory,
    extract_audio_metadata,
    separate_audio_stems,
    merge_audio_stems,
    transcribe_audio_lyrics
)

# Initialize Logger
logger = logging.getLogger(__name__)


# Handler Functions
def handle_audio_processing(
        input_file: Union[str, Path],
        cache_dir: Union[str, Path],
        override_meta: bool = False,
        override_audio: bool = False,
        override_transcribe: bool = False,
        beam_size_input: int = 15,
        best_of_input: int = 5,
        patience_input: float = 3.0,
        condition_toggle: bool = False,
        compression_threshold_input: float = 1.3,
        temperature_input: float = 0.0,
        language_input: str = "Auto Detect",
        file_name: str = "raw_lyrics.json",
):
    """
    Handler function to process the audio file.
    1) Initializes the working directory.
    2) Extracts song metadata.
    3) Performs audio stem separation.
    4) Merges audio stems into a single karaoke audio.
    5) Extracts raw lyrics using Whisper Language Model.
    6) Returns the path to the raw lyrics file and the working directory.
    """
    try:
        # Initialize working directory
        working_dir, file_hash = initialize_working_directory(input_file, cache_dir)

        # Extract Song Metadata
        # Query audio file metadata from AcoustID API (title and artist) and store in a JSON file
        title, artists = extract_audio_metadata(input_file, working_dir, override=override_meta)

        # Perform Audio Stem Separation
        # Extract vocals, other, bass, and drums from the input audio file using Demucs from Facebook AI
        # Re-arrange the files in the working directory
        separate_audio_stems(input_file, working_dir, override=override_audio)

        # Merge Audio Stems into a single Karaoke Audio
        # Merge the other, bass, and drums into a single karaoke audio file using AudioSegment from PyDub
        merge_audio_stems(working_dir, override=override_audio)

        # Extract Raw Lyrics
        # Extract the segments (lyric transcription, timing, and confidence scores) using the Whisper OpenAI API
        # Reformat the data into a JSON file
        raw_lyrics_path = transcribe_audio_lyrics(
            working_dir,
            override=override_transcribe,
            beam_size_input=beam_size_input,
            best_of_input=best_of_input,
            patience_input=patience_input,
            condition_toggle=condition_toggle,
            compression_threshold_input=compression_threshold_input,
            temperature_input=temperature_input,
            language_option=language_input,
            file_name=file_name,
        )

        return raw_lyrics_path, working_dir, title, artists

    except Exception as e:
        raise RuntimeError(f"Error in audio processing pipeline: {e}")
