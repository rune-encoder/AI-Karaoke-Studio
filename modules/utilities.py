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


def load_json(file_path: Path) -> dict:
    with open(file_path, "r") as file:
        return json.load(file)


def save_json(data: dict, file_path: Path) -> None:
    with open(file_path, "w") as file:
        json.dump(data, file, indent=4)
