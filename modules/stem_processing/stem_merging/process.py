from pathlib import Path
from typing import Union
import logging

from .main import _merge_audio_stems

logging.basicConfig(level=logging.INFO)

def process_audio_merging(
    output_path: Union[str, Path],
    override: bool = False,
    file_name: str = "instrumental.mp3"
):

    output_file = Path(f"{output_path}/{file_name}")

    if output_file.exists() and not override:
        logging.info("Instrumental already exists. Skipping merge...")
        return

    try:
        _merge_audio_stems(stems_directory=output_path, output_file=output_file)

    except Exception as e:
        logging.error(f"An error occurred during audio merging: {e}")
