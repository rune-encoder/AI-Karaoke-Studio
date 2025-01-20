# Standard Library Imports
from pathlib import Path
from typing import Union
import logging

# Local Application Imports
from .main import _audio_stem_separation

# Initialize Logger
logger = logging.getLogger(__name__)


def process_audio_stem_separation(
    input_file: Union[str, Path],
    output_path: Union[str, Path],
    override: bool = False
):
    expected_stems = ['vocals', 'drums', 'bass', 'other']

    # Check if any of the expected stem files already exist in the directory and
    # skip the separation if the override flag is not set
    if not override:
        for file in Path(output_path).iterdir():
            if file.is_file() and file.stem.lower() in expected_stems:
                logger.info(
                    "Skipping stem separation... Audio stems already exist in the output directory...")
                return

    # Perform audio stem separation
    _audio_stem_separation(
        input_file,
        output_path,
    )
