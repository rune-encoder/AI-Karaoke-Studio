# Standard Library Imports
from pathlib import Path
from typing import Union
import logging

# Local Application Imports
from .main import _merge_audio_stems

# Initialize Logger
logger = logging.getLogger(__name__)


def process_audio_merging(
    output_path: Union[str, Path],
    override: bool = False,
    file_name: str = "instrumental.mp3"
):
    # Check if the instrumental audio file already exists in the output directory and
    # skip the merging if the override flag is not set
    output_file = Path(f"{output_path}/{file_name}")
    if output_file.exists() and not override:
        logger.info(
            "Skipping audio merging... Instrumental audio already exists in the output directory...")
        return

    # Merge audio stems
    _merge_audio_stems(stems_directory=output_path, output_file=output_file)
