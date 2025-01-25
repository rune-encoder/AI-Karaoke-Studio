# Standard Library Imports
from pathlib import Path
from typing import Union
import logging
import json
import os

# Third-Party Imports
import acoustid

# Local Application Imports
from modules.utilities import normalize_path

# Initialize Logger
logger = logging.getLogger(__name__)

# AcoustID API Key
ACOUSTID_API_KEY = os.getenv('ACOUST_ID')


def _extract_audio_metadata(
    audio_path: Union[str, Path],
    output_directory: Union[str, Path],
    file_name: str = "metadata.json"
):
    try:
        # Generate fingerprint and duration for the input audio file
        duration, fingerprint = acoustid.fingerprint_file(audio_path)
        logging.debug(
            f"Generated fingerprint and duration: {duration}, {fingerprint}")

        # Decode the fingerprint from bytes to string if necessary
        if isinstance(fingerprint, bytes):
            fingerprint = fingerprint.decode('utf-8')

        # Query AcoustID API and search for the best matching audio
        result = acoustid.lookup(ACOUSTID_API_KEY, fingerprint, int(duration))
        logging.debug(f"AcoustID lookup result: {result}")

        # Check if there is no match found, log a warning and return
        if not result.get('results', []):
            logging.warning(f"No match found for: {audio_path}")
            return

        # Extract metadata from the best match
        best_match = result['results'][0]
        recordings = best_match.get('recordings', [])

        metadata = {
            "fingerprint": fingerprint,
            "duration": duration,
            "title": "Unknown Title",
            "artists": ["Unknown Artist"],
            "albums": ["Unknown Album"],
            "score": best_match.get('score', 0)
        }

        if recordings:
            # Get the first recording
            recording = recordings[0]  

            # Update metadata with the recording details
            metadata["title"] = recording.get('title', metadata["title"])
            metadata["artists"] = [artist.get(
                'name', 'Unknown Artist') for artist in recording.get('artists', [])]
            metadata["albums"] = [release.get(
                'title', 'Unknown Album') for release in recording.get('releasegroups', [])]

        # Save metadata to a file named metadata.json
        output_file = os.path.join(output_directory, file_name)
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=4, ensure_ascii=False)

        logger.info(f"Audio metadata extracted successfully!")

    except Exception as e:
        logging.error(f"Error processing audio file: {e}", exc_info=True)
        raise RuntimeError(f"Error processing audio file: {e}")
