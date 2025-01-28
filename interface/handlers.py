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
        override_all: bool = False,
        file_name: str = "raw_lyrics.json"
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
        extract_audio_metadata(input_file, working_dir, override=override_all)

        # Perform Audio Stem Separation
        # Extract vocals, other, bass, and drums from the input audio file using Demucs from Facebook AI
        # Re-arrange the files in the working directory
        separate_audio_stems(input_file, working_dir, override=override_all)

        # Merge Audio Stems into a single Karaoke Audio
        # Merge the other, bass, and drums into a single karaoke audio file using AudioSegment from PyDub
        merge_audio_stems(working_dir, override=override_all)

        # Extract Raw Lyrics
        # Extract the segments (lyric transcription, timing, and confidence scores) using the Whisper OpenAI API
        # Reformat the data into a JSON file
        raw_lyrics_path = transcribe_audio_lyrics(
            working_dir,
            override=override_all,
            file_name=file_name
        )

        return raw_lyrics_path, working_dir

    except Exception as e:
        raise RuntimeError(f"Error in audio processing pipeline: {e}")
