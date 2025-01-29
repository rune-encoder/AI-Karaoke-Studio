# Standard Library Imports
from pathlib import Path
from typing import Union
import logging

# Local Application Imports
from .main import _excecute_stem_merge

# Initialize Logger
logger = logging.getLogger(__name__)


def merge_audio_stems(
    working_dir: Union[str, Path],
    override: bool = False,
    file_name: str = "karaoke_audio.mp3"
):
    """Merge audio stems into a karaoke instrumental."""
    # Check if the instrumental audio file already exists in the output directory and
    # skip the merging if the override flag is not set
    output_file = Path(working_dir) / file_name
    if output_file.exists() and not override:
        logger.info("Skipping audio merging... Karaoke audio already exists in the output directory.")
        return

    try:
        logger.info(f"Merging audio stems into a single karaoke audio file: {output_file.stem}")
        _excecute_stem_merge(stems_directory=working_dir, output_file=output_file)
        logger.info("Audio stems merged successfully.")
        return
    
    except Exception as e:
        raise RuntimeError(f"Error in audio merging: {e}")
