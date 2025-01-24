
# Standard Library Imports
from pathlib import Path
from typing import Union
import logging
from pprint import pprint

# Local Application Imports
from .config import get_available_colors, get_font_list
from .utilities import extract_audio_duration
from ..utilities import load_json, save_json
from .create_ass_file import create_ass_file

# Initialize Logger
logger = logging.getLogger(__name__)

def process_karaoke_subtitles(
    output_path: Union[str, Path],
    override: bool = False,
    file_name: str = "karaoke_subtitles.ass"
):
    try:
        modified_lyrics_file = Path(output_path) / "modified_ai_lyrics.json"
        raw_lyrics_file = Path(output_path) / "raw_lyrics.json"
        audio_file = Path(output_path) / "instrumental.mp3"
        output_file = Path(output_path) / file_name

        # Check if the output file already exists and skip if override is not set
        if output_file.exists() and not override:
            logger.info(
                "Skipping subtitle generation... Karaoke subtitles file already exists in the output directory."
            )
            return
        
        lyrics_file = modified_lyrics_file if Path(modified_lyrics_file).exists() else Path(raw_lyrics_file)

        if not lyrics_file.exists():
            logger.error(f"Lyrics file does not exist. Skipping subtitle generation...")
            return
        
        # Load the lyrics
        lyrics = load_json(lyrics_file)
        pprint(lyrics, sort_dicts=False)

        # Extract audio duration (assuming you have an input file for the instrumental audio)
        audio_duration = extract_audio_duration(audio_file)
        print(audio_duration)

        if audio_duration is None:
            raise ValueError(f"Could not extract audio duration from {audio_duration}")

        for verse in lyrics:
            if verse['start'] is None or verse['end'] is None:
                logger.error(f"Verse {verse['verse_number']} has invalid start or end times. Skipping this verse...")
                continue
            for word in verse['words']:
                if word['start'] is None or word['end'] is None:
                    logger.error(f"Word {word['word_number']} in verse {verse['verse_number']} has invalid start or end times. Skipping this word...")
                    continue


        create_ass_file(
            lyrics,
            output_path=output_file,
            audio_duration=audio_duration,
            font="Arial",  # Example font
            fontsize=24,  # Example font size
            title="Karaoke",  # Example title
            primary_color="White",
            secondary_color="Yellow"
        )
        logger.info(f"Karaoke subtitles file created: {output_file}")

    except Exception as e:
        logger.error(f"An error occurred during subtitle generation: {e}")
        raise

