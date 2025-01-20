# Standard Library Imports
from pydub import AudioSegment
from pathlib import Path
from typing import Union
import logging

# Initialize Logger
logger = logging.getLogger(__name__)


def _merge_audio_stems(
    stems_directory: Union[str, Path],
    output_file: Union[str, Path],
    output_format: str = 'mp3'
):
    # Define the expected stem file names
    expected_files = ['bass', 'drums', 'other']
    stem_files = {}

    # Iterate through the files in the directory and find the required stems
    for file in Path(stems_directory).iterdir():
        if file.is_file():
            stem_name = file.stem.lower()
            if stem_name in expected_files:
                stem_files[stem_name] = file

    # Validate that all required audio stem paths are found
    if not all(stem in stem_files for stem in expected_files):
        logger.error(
            "All required stem files (bass, drums, other) must be provided.")
        raise ValueError(
            "All required stem files (bass, drums, other) must be provided.")

    try:
        # Step 1: Load the audio stems
        # Each stem (bass, drums, other, vocals) is loaded as an AudioSegment object
        stems = [AudioSegment.from_file(stem_files[stem])
                 for stem in expected_files]

        # Step 2: Merge the stems by overlaying them sequentially
        # Start with the first stem (bass) and overlay the rest (drums, other, vocals) one by one
        merged_audio = stems[0]
        for stem in stems[1:]:
            merged_audio = merged_audio.overlay(stem)

        # Step 3: Export the merged audio to the specified format
        merged_audio.export(output_file, format=output_format)
        logger.info(f"Audio stems merged successfully!")

    except Exception as e:
        logger.error(f"Error in merging audio stems: {e}")
        raise RuntimeError(f"Error in merging audio stems: {e}")
