# Standard Library Imports
from pathlib import Path
from typing import Union
import logging
import json

# Initialize Logger
logger = logging.getLogger(__name__)


# ════════════════════════════════════════════════════════════
# HELPER FUNCTIONS
# ════════════════════════════════════════════════════════════
def normalize_path(path):
    return str(Path(path).resolve())


def load_json(file_path: Path) -> dict:
    with open(file_path, "r") as file:
        return json.load(file)


def save_json(data: dict, file_path: Path) -> None:
    with open(file_path, "w") as file:
        json.dump(data, file, indent=4)


def ensure_directory_exists(directory: Union[str, Path]) -> Path:
    """
    Ensure that a directory exists. If it does not, create it (including any missing parent directories).

    Args:
        directory (Union[str, Path]): Path to the directory that should be checked or created.

    Returns:
        Path: A Path object representing the ensured directory.

    Notes:
        - If the directory already exists, this function does nothing.
        - If the directory does not exist, it is created, including all necessary parent directories.
    """
    # Convert the input to a Path object
    directory = Path(directory)

    # Create the directory if it does not exist
    directory.mkdir(parents=True, exist_ok=True)

    # Return the Path object for further use
    return directory