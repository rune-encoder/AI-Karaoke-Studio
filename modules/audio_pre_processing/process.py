# Standard Library Imports
from pathlib import Path
from typing import Union
import logging

# Local Application Imports
from .main import _extract_audio_metadata
from .utilities import (
    _create_directory,
    _validate_audio_file,
    _get_file_hash,
)

# Initialize Logger
logger = logging.getLogger(__name__)


def pre_process_audio_file(
    input_file: Union[str, Path],
    output_path: Union[str, Path],
    override: bool = False,
    file_name: str = "metadata.json"
):
    # Confirm the file is a valid audio file
    if not _validate_audio_file(input_file):
        raise ValueError(f"Invalid audio file: {input_file}. Please provide a valid audio file.")

    file_hash = _get_file_hash(input_file)
    working_dir = _create_directory(Path(output_path) / file_hash)
    logger.info(f"Cache Directory: {working_dir}")

    # Check if the audio metadata file already exists in the output directory and
    # skip the extraction if the override flag is not set
    output_file = Path(working_dir) / file_name
    if output_file.exists() and not override:
        logger.info(
            "Skipping audio pre-processing... Audio metadata already exist in the output directory...")
        return working_dir

    # Extract audio metadata from the input audio file
    _extract_audio_metadata(input_file, working_dir, file_name)

    return working_dir
