# ════════════════════════════════════════════════════════════
# IMPORTS
# ════════════════════════════════════════════════════════════
from pathlib import Path
import logging
import hashlib
from typing import Union
from .config import EXTENSIONS

logging.basicConfig(level=logging.INFO)

# ════════════════════════════════════════════════════════════
# HELPER FUNCTIONS
# ════════════════════════════════════════════════════════════
def normalize_path(path):
    return str(Path(path).resolve())


def create_directory(path):
    """
    Create a directory if it does not exist.

    Args:
        path (str): Path to the directory.
    """
    path = Path(path)

    # Create the directory if it does not exist
    if not path.exists():
        path.mkdir(parents=True, exist_ok=True)
        logging.info(f"Created directory: {path}")
    else:
        logging.debug(f"Directory already exists: {path}")
    return path


def ensure_file_exists(file_path: Union[str, Path], error_message: str = "File not found"):
    """
    Ensure that a file exists at the specified path.

    Args:
        file_path (Union[str, Path]): Path to the file.
        error_message (str): Error message to display if the file is not found.
    """
    if not Path(file_path).exists():
        raise FileNotFoundError(f"{error_message}: {file_path}")


def validate_audio_file(file_path):
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
        logging.error(f"Audio file not found: {file_path}")
        return False
    
    if file.suffix.lower().lstrip(".") not in EXTENSIONS:
        logging.error(f"Unsupported file extension: {file.suffix}")
        return False
    return True


def get_file_hash(file_path):
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
    return hash_func.hexdigest()