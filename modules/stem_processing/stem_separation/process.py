# Standard Library Imports
from pathlib import Path
from typing import Union
import logging

# Local Application Imports
from .main import _excecute_stem_separation

# Initialize Logger
logger = logging.getLogger(__name__)


def separate_audio_stems(
    input_file: Union[str, Path],
    working_dir: Union[str, Path],
    override: bool = False
):
    """Perform stem separation and save results in the working directory."""
    expected_stems = ['vocals', 'drums', 'bass', 'other']

    # Check if any of the expected stem files already exist in the directory and
    # skip the separation if the override flag is not set
    if not override:
        existing_stems = [f.stem.lower() for f in working_dir.iterdir() if f.is_file()]
        if all(stem in existing_stems for stem in expected_stems):
            logger.info("Stems already exist. Skipping stem separation...")
            return

    try:
        logger.info(f"Separating audio stems for input file: {Path(input_file).stem}")
        _excecute_stem_separation(input_file, working_dir)
        logger.info(f"Audio stems separated successfully!")
        return
        
    except Exception as e:
        raise RuntimeError(f"Error in stem separation: {e}")
