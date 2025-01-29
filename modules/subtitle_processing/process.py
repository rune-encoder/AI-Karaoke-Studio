# Standard Library Imports
from pathlib import Path
from typing import Union
import logging

# Local Application Imports
from .utilities import extract_audio_duration
from ..utilities import load_json
from .create_ass_file import create_ass_file

# Initialize Logger
logger = logging.getLogger(__name__)


def process_karaoke_subtitles(
    output_path: Union[str, Path],
    override: bool = False,
    file_name: str = "karaoke_subtitles.ass",
    font: str = "Arial",
    fontsize: int = 24,
    primary_color: str = "White",
    secondary_color: str = "Yellow",
    outline_color: str = "Black",
    outline_size: int = 2,
    shadow_color: str = "Black",
    shadow_size: int = 0,
    screen_width: int = 1280, 
    screen_height: int = 720,
    verses_before: int = 1,
    verses_after: int = 1,
):
    try:
        logger.info(f"Creating karaoke subtitle file referencing timed lyrics")

        metadata = Path(output_path) / "metadata.json"
        modified_lyrics_file = Path(output_path) / "modified_lyrics.json"
        raw_lyrics_file = Path(output_path) / "raw_lyrics.json"
        audio_file = Path(output_path) / "karaoke_audio.mp3"
        output_file = Path(output_path) / file_name

        # Check if the output file already exists and skip if override is not set
        if output_file.exists() and not override:
            logger.info("Skipping subtitle generation... Karaoke subtitles file already exists in the output directory.")
            return

        # Use `modified_lyrics.json`. If it does not exist use `raw_lyrics.json`
        lyrics_file = modified_lyrics_file if Path(modified_lyrics_file).exists() else Path(raw_lyrics_file)

        if not lyrics_file.exists():
            logger.error(f"Lyrics file does not exist. Skipping subtitle generation...")
            raise FileNotFoundError(f"Lyrics file '{lyrics_file}' does not exist.")

        # Load the artist info
        artist_info = load_json(metadata)
        song_name = artist_info.get("title", "Unknown Title")
        artist_name = artist_info.get("artists", ["Unknown Artist"])[0]
        title = f"{artist_name}\n~ {song_name} ~\nKaraoke"
        title = title.replace("\n", r"\N")

        # Load the lyrics
        verses_data = load_json(lyrics_file)

        # Extract audio duration (assuming you have an input file for the instrumental audio)
        audio_duration = extract_audio_duration(audio_file)

        if audio_duration is None:
            raise ValueError(f"Could not extract audio duration from {audio_duration}")

        create_ass_file(
            verses_data,
            output_path=output_file,
            audio_duration=audio_duration,
            font=font,
            fontsize=fontsize,
            primary_color=primary_color,
            secondary_color=secondary_color,
            outline_color=outline_color,
            outline_size=outline_size,
            shadow_color=shadow_color,
            shadow_size=shadow_size,
            title=title,
            screen_width=screen_width,
            screen_height=screen_height,
            verses_before=verses_before,
            verses_after=verses_after,
        )

        logger.info(f"Karaoke subtitles file created: {output_file}")

    except Exception as e:
        logger.error(f"An error occurred during subtitle generation: {e}")
        raise
