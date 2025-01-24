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


def ensure_file_exists(file_path: Union[str, Path], error_message: str = "File not found"):
    """
    Ensure that a file exists at the specified path.

    Args:
        file_path (Union[str, Path]): Path to the file.
        error_message (str): Error message to display if the file is not found.
    """
    if not Path(file_path).exists():
        logger.error(f"{error_message}: {file_path}")
        raise FileNotFoundError(f"{error_message}: {file_path}")

    from pathlib import Path


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


def get_project_root() -> Path:
    """
    Locate the root of the project dynamically by searching for a marker file or folder.

    This function traverses up the directory tree, starting from the current file's location,
    and looks for markers like `.git` or `requirements.txt` to identify the project root.

    Returns:
        Path: The Path object representing the root of the project.

    Raises:
        FileNotFoundError: If no project root marker is found in any parent directory.

    Notes:
        - Adjust the marker files/folders (`.git`, `requirements.txt`) as per your project's structure.
    """
    # Start from the current file's directory
    current_path = Path(__file__).resolve()

    # Traverse upwards in the directory tree
    while current_path.parent != current_path:

        # Check for marker files or folders
        if (current_path / ".git").exists() or (current_path / "requirements.txt").exists():
            return current_path
        
        # Move to the parent directory
        current_path = current_path.parent

    logger.debug(f"Checking project root: {current_path}")

    # Raise an error if no markers are found
    raise FileNotFoundError(
        "Project root not found. Ensure a marker file (e.g., .git or requirements.txt) exists in the root."
    )