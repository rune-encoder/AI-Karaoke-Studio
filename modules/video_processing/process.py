
# Standard Library Imports
from pathlib import Path
from typing import Union
import logging
from pprint import pprint
import re

from .main import generate_karaoke_video
from ..utilities import load_json

logger = logging.getLogger(__name__)

def normalize_path(path):
    return str(Path(path).resolve())

def process_karaoke_video(
    working_dir: Union[str, Path],
    output_path: Union[str, Path],

    resolution: str = "1280x720",
    preset: str = "fast",
    crf: int = 23,
    fps: int = 24,
    bitrate: str = "3000k",
    audio_bitrate: str = "192k",
):
    metadata_file = Path(working_dir) / "metadata.json"
    karaoke_audio = Path(working_dir) / "karaoke_audio.mp3"
    # karaoke_audio = Path(r"C:\Users\chris\ai_karaoke_app\input\play_minstrel_play.mp3")
    karaoke_subtitles = Path(working_dir) / "karaoke_subtitles.ass"

    try:
        # Load the audio metadata file
        metadata = load_json(metadata_file)

        # Remove parentheses and their contents
        title = re.sub(r"\(.*?\)", "", metadata["title"]).strip()

        # Replace non-alphanumeric characters with underscores and convert to lowercase
        sanitized_title = re.sub(r'[^a-zA-Z0-9]+', '_', title).lower()

        # Relative paths for FFmpeg
        relative_subtitles = karaoke_subtitles.relative_to(working_dir.parent.parent)
        relative_output = Path(output_path.name) / f"{sanitized_title}_karaoke.mp4"

        generate_karaoke_video(
            audio_path=karaoke_audio.as_posix(),
            ass_path=relative_subtitles.as_posix(),
            output_path=relative_output.as_posix(),

            resolution=resolution,
            preset=preset,
            crf=crf,
            fps=fps,
            bitrate=bitrate,
            audio_bitrate=audio_bitrate
        )

        return relative_output

    except Exception as e:
        logger.error(f"Error loading metadata: {e}")
        raise
