# Standard Library Imports
from pathlib import Path
from typing import Union
import logging
import json
import os

# Third-Party Imports
from dotenv import load_dotenv
import acoustid

# Local Application Imports
from modules.utilities import normalize_path

# Initialize Logger
logger = logging.getLogger(__name__)

# AcoustID API Key
load_dotenv()
ACOUSTID_API_KEY = os.getenv('ACOUST_ID')


def _fetch_audio_metadata(
    audio_path: Union[str, Path],
    output_directory: Union[str, Path],
    file_name: str = "metadata.json"
):
    """
    Extracts metadata from the audio file using AcoustID and saves it as metadata.json.
    If the lookup fails, default metadata with 'Unknown' fields is saved.

    Args:
        audio_path (Union[str, Path]): Path to the input audio file.
        output_directory (Union[str, Path]): Directory to save the metadata JSON file.
        file_name (str): Name of the metadata file.

    Returns:
        bool: True if metadata was successfully saved, False otherwise.
    """

    try:
        # Initialize default metadata
        metadata = {
            "fingerprint": "Unknown",
            "duration": 0,
            "title": "Unknown Title",
            "artists": ["Unknown Artist"],
            "albums": ["Unknown Album"],
            "score": 0,
            "retrieved_successfully": False,
        }

        try:
            # Generate fingerprint and duration for the input audio file by using Chromaprint fpcalc
            duration, fingerprint = acoustid.fingerprint_file(audio_path)
            logger.debug(f"Generated fingerprint and duration: {duration}, {fingerprint}")

            # Update metadata with the generated fingerprint and duration
            metadata["fingerprint"] = fingerprint.decode('utf-8') if isinstance(fingerprint, bytes) else fingerprint
            metadata["duration"] = duration

        except Exception as e:
            logger.warning(f"Failed to generate fingerprint and duration: {e}")

        try:
            # Query AcoustID API and search for the best matching audio
            result = acoustid.lookup(ACOUSTID_API_KEY, metadata["fingerprint"], int(metadata["duration"]))
            logger.debug(f"AcoustID lookup result: {result}")

            # Check if there is a match found and obtain the best matching audio details
            if result.get('results', []):
                best_match = result['results'][0]
                recordings = best_match.get('recordings', [])

                # Update metadata with the best match details
                metadata["score"] = best_match.get('score', metadata["score"])

                # If there are recordings, update metadata with the first recording details
                if recordings:
                    recording = recordings[0]
                    metadata["title"] = recording.get('title', metadata["title"])
                    metadata["artists"] = [artist.get('name', metadata["artists"]) for artist in recording.get('artists', [])]
                    metadata["albums"] = [release.get('title', metadata["albums"]) for release in recording.get('releasegroups', [])]

                # Mark metadata as successfully retrieved
                metadata["retrieved_successfully"] = True
            else:
                logger.warning(f"No match found for: {audio_path}")

        except Exception as e:
            logger.warning(f"AcoustID lookup failed: {e}")

        # Save metadata to a file named metadata.json
        output_file = Path(output_directory) / file_name
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=4, ensure_ascii=False)

        logger.info(f"Audio metadata saved successfully to {output_file}")
        return metadata["title"], metadata["artists"]

    except Exception as e:
        logger.error(f"Error processing audio file: {e}", exc_info=True)
        return metadata["title"], metadata["artists"]
