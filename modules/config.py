# Standard Library Imports
from pathlib import Path
import logging

# Initialize Logger
logger = logging.getLogger(__name__)


def _get_project_root() -> Path:
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


def initialize_directories():
    """Set up and return important project directories."""

    project_root = _get_project_root()
    cache_dir = project_root / "cache"
    fonts_dir = project_root / "fonts"
    output_dir = project_root / "output"

    # Ensure that the cache and output directories exist
    cache_dir.mkdir(parents=True, exist_ok=True)
    fonts_dir.mkdir(parents=True, exist_ok=True)
    output_dir.mkdir(parents=True, exist_ok=True)

    return project_root, cache_dir, fonts_dir, output_dir
