# Standard Library Imports
from pathlib import Path
from typing import Union
import logging

# Local Application Imports
from .stem_processing import (process_audio_merging, process_audio_stem_separation)
from .lyrics_processing import (process_audio_extract_lyric_timing, process_lyric_search, process_lyrics_modification)
from .audio_pre_processing import pre_process_audio_file
from .logging_config import configure_logging
from .subtitle_processing import process_karaoke_subtitles
from .utilities import (get_project_root, ensure_directory_exists)

# Initialize Logger
logger = logging.getLogger(__name__)

# Pipeline Controller
def run_pipeline(
    input_file: Union[str, Path],
    override_all: bool = False,
    verbose: bool = False,
):
    # 1. Configure logging based on the verbose flag
    configure_logging(verbose)

    project_root = get_project_root()
    cache_dir = ensure_directory_exists(project_root / "cache")
    output_dir = ensure_directory_exists(project_root / "output")

    # 1. Validate input song file
    # 2. Obtain song file hash 
    # 3. Create a cache dir to store the working files
    # 4. Query audio file metadata from AcoustID API (title and artist)
    working_dir = pre_process_audio_file(
        input_file,
        cache_dir,
        override=override_all
    )

    # 1. Extract vocals, other, bass, and drums from the input audio file
    # using Demucs from Facebook AI
    # 2. Re-arrange the files in the working directory
    process_audio_stem_separation(
        input_file, working_dir, override=override_all)

    # using AudioSegment from PyDub
    # 1. Merge the other, bass, and drums into a single karaoke audio file
    # using AudioSegment from PyDub
    process_audio_merging(working_dir, override=override_all)

    # 1. Extract the segments (lyric transcription, timing, and confidence scores) 
    # using the Whisper OpenAI API
    # 2. Reformat the data into a JSON file
    process_audio_extract_lyric_timing(working_dir, override=override_all)

    # 1. Query the lyrics from the Genius API using the file metadata
    # obtaining a URL for the lyrics
    # 2. Scrape the lyrics from the Genius webpage
    # 3. Clean the lyrics and save them as a JSON file
    process_lyric_search(working_dir, override=override_all)

    # 1. Condense raw transcription and official lyrics and send in chunks updating
    # the prompt to Google Gemeni API
    # 2. Clean the resonse, parse the response, reformat the data into a JSON file
    process_lyrics_modification(working_dir, override=override_all)

    # process_karaoke_subtitles(working_dir, override=override_all)
