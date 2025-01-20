import logging
from pathlib import Path
from typing import Union

from .main import _audio_stem_separation

logging.basicConfig(level=logging.INFO)

def process_audio_stem_separation(
    input_file: Union[str, Path],
    output_path: Union[str, Path],
    override: bool = False
):
    expected_stems = ['vocals', 'drums', 'bass', 'other']

    # Check if any of the expected stem files already exist in the directory
    if not override:
        for file in Path(output_path).iterdir():
            if file.is_file() and file.stem.lower() in expected_stems:
                logging.info(
                    "Stem files already exist. Use override=True to regenerate them.")
                return

    _audio_stem_separation(
        input_file,
        output_path,
    )
