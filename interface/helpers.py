# Standard Library Imports
from typing import List, Union
from pathlib import Path
import logging
import json

# Third-Party Imports
import pandas as pd
import gradio as gr
from deep_translator import GoogleTranslator

# Initialize logger
logger = logging.getLogger(__name__)


# Helper Functions
def load_json_file(file_path: Union[str, Path]) -> Union[List, dict, None]:
    """
    Safely loads a JSON file into Python data structure.
    Returns None if file not found or error.
    """
    try:
        file_path = Path(file_path)
        if not file_path.exists():
            return None

        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Could not load JSON file {file_path}: {e}")
        return None


def save_json_file(data, file_path: Union[str, Path]):
    """
    Save Python data structure as a JSON file.
    Overwrites if file exists.
    """
    try:
        file_path = Path(file_path)

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

    except Exception as e:
        logger.error(f"Could not save JSON to {file_path}: {e}")
        raise


def get_effect_video_list(effects_dir: Union[str, Path]) -> list:
    """
    Scans the 'effects_dir' folder for .mp4 files
    and returns a list of file names (e.g. ["snow.mp4", "fire.mp4", ...])
    """
    effects_dir = Path(effects_dir)
    if not effects_dir.exists() or not effects_dir.is_dir():
        return []

    # Gather .mp4
    video_files = [f.name for f in effects_dir.glob("*.mp4") if f.is_file()]
    return video_files


def get_available_languages():
    """
    Retrieve available language codes and names for translation.
    
    Returns:
        dict: Dictionary of language names and codes.
    """ 
    # Get languages as a dictionary from GoogleTranslator
    g_translator = GoogleTranslator()
    
    return g_translator.get_supported_languages(as_dict=True)


def display_text_from_lyrics(json_file: Union[str, Path]) -> str:
    """
    Groups words by verse and returns a user-friendly multiline string.
    """
    try:
        with open(json_file, "r") as f:
            metadata = json.load(f)

        # Group words by verse for display
        grouped_by_verse = {}
        for verse_info in metadata:
            verse_number = verse_info["verse_number"]
            if verse_number not in grouped_by_verse:
                grouped_by_verse[verse_number] = []
            for w in verse_info.get("words", []):
                grouped_by_verse[verse_number].append(w["word"])

        # Create display text for the verses
        verse_texts = []
        for verse_num, words_list in grouped_by_verse.items():
            line = " ".join(words_list)
            verse_texts.append(f"Verse {verse_num}: {line}")

        # Join them with newlines
        display_text = "\n".join(verse_texts)
        return display_text
    
    except Exception as e:
        logger.error(f"Error generating display lyrics: {e}")
        return f"Error: {e}"


def display_dataframe_from_lyrics(json_path: Union[str, Path]) -> pd.DataFrame:
    """
    Loads raw_lyrics.json (or modified_lyrics.json) 
    and converts to a Pandas DataFrame with a single column:
    - Lyrics (the combined text)
    """
    try:
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        rows = []
        for verse_info in data:
            # Option 1: Use the "text" field directly if it already has full verse text
            # verse_text = verse_info.get("text", "")

            # Option 2: Or combine the words array if you want them re-joined:
            verse_text = " ".join(w["word"] for w in verse_info["words"])

            rows.append({"Processed Lyrics (Used for Karaoke)": verse_text})

        df = pd.DataFrame(rows)
        return df
    except Exception as e:
        print(f"Error reading {json_path}: {e}")
        return pd.DataFrame(columns=["Lyrics"])


def check_modify_ai_availability(working_dir: str) -> dict:
    """
    Returns a dict instructing Gradio to update the 'Modify with AI' button 
    so it is enabled (interactive=True) only if:
     - raw_lyrics.json exists, AND
     - reference_lyrics.json (or official_lyrics.json) exists.
    Otherwise, disable it.
    """
    if not working_dir:
        return gr.update(interactive=False)  # No working dir -> disable
    
    wd = Path(working_dir)
    raw_path = wd / "raw_lyrics.json"
    ref_path = wd / "reference_lyrics.json"

    if raw_path.is_file() and ref_path.is_file():
        # Both files exist -> enable button
        return gr.update(interactive=True)
    else:
        # Something missing -> disable
        return gr.update(interactive=False)


def check_generate_karaoke_availability(working_dir: str) -> dict:
    """
    Returns a dict instructing Gradio to update the 'Generate Karaoke' button 
    so it is enabled only if either:
     - raw_lyrics.json exists, OR
     - modified_lyrics.json exists.
    Otherwise, disable it.
    """
    if not working_dir:
        return gr.update(interactive=False)
    
    wd = Path(working_dir)
    raw_path = wd / "raw_lyrics.json"
    modified_path = wd / "modified_lyrics.json"

    if raw_path.is_file() or modified_path.is_file():
        # At least one of them exists -> enable
        return gr.update(interactive=True)
    else:
        return gr.update(interactive=False)