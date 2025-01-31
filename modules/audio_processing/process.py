# Standard Library Imports
from pathlib import Path
import logging
import json

# Local Application Imports
from .main import _fetch_audio_metadata
from .utilities import (
    _create_directory,
    _validate_audio_file,
    _get_file_hash,
)

# Initialize Logger
logger = logging.getLogger(__name__)


def initialize_working_directory(
        input_file: Path,
        cache_dir: Path,
):
    """Initialize the working directory for the input file."""
    # Confirm the file is a valid audio file
    if not _validate_audio_file(input_file):
        raise ValueError(f"Invalid audio file: {input_file}. Please provide a valid audio file.")
    
    logger.info(f"Initializing working directory for input file: {Path(input_file).stem}")
    file_hash = _get_file_hash(input_file)
    working_dir = _create_directory(cache_dir / file_hash)
    logger.info(f"Working directory initialized: {working_dir}")
    return working_dir, file_hash


def extract_audio_metadata(
        input_file: Path,
        working_dir: Path,
        override: bool = False,
        file_name: str = "metadata.json"
):
    """Extract and save audio metadata using AcoustID API."""
    # Check if the audio metadata file already exists in the output directory and
    # skip the extraction if the override flag is not set
    metadata_file = Path(working_dir) / file_name
    if metadata_file.exists() and not override:
        logger.info("Song metadata already exist. Skipping api query and extraction of audio data...")
        with open(metadata_file, 'r') as file:
            metadata = json.load(file)
        return metadata["title"], metadata["artists"]

    try:
        logger.info(f"Extracting audio metadata for input file: {Path(input_file).stem}")
        title, artists = _fetch_audio_metadata(input_file, working_dir, file_name)
        return title, artists
    
    except Exception as e:
        logger.warning(f"Metadata extraction failed: {e}. Proceeding without metadata.")
        return