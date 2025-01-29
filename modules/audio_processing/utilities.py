# Standard Library Imports
from .config import EXTENSIONS
from pathlib import Path
import logging
import hashlib

# Initialize Logger
logger = logging.getLogger(__name__)


def _create_directory(path):
    """
    Create a directory if it does not exist.

    Args:
        path (str): Path to the directory.
    """
    path = Path(path)

    # Create the directory if it does not exist
    if not path.exists():
        path.mkdir(parents=True, exist_ok=True)
        logger.debug(f"Created directory: `./{path.stem}`")
    return path


def _get_file_hash(file_path):
    """
    Generate a SHA256 hash of a file's content.
    Once all chunks have been read and processed, finalize 
        the hash and get the hexadecimal representation.
    Args:
        file_path (str): Path to the file.
    Returns:
        str: Hexadecimal hash of the file.
    """
    # Create a new SHA256 hash object
    hash_func = hashlib.sha256()

    # Open the file in binary read mode
    with open(file_path, 'rb') as f:

        # Read the file in chunks of 8192 bytes
        while chunk := f.read(8192):

            # Update the hash object with the chunk
            hash_func.update(chunk)

    # Return the hexadecimal representation of the hash
    logger.debug(f"File hash: {hash_func.hexdigest()}")
    return hash_func.hexdigest()


def _validate_audio_file(file_path):
    """
    Validate the existence and extension of an audio file.

    Args:
        file_path (str): Path to the audio file.

    Returns:
        bool: True if the file is valid, False otherwise.
    """
    file = Path(file_path)

    # Check if the file exists and has a valid extension
    if not file.exists():
        logger.error(f"Audio file not found: {file_path}")
        return False

    if file.suffix.lower().lstrip(".") not in EXTENSIONS:
        logger.error(f"Unsupported file extension: {file.suffix}")
        return False
    return True
