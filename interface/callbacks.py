# Standard Library Imports
from typing import Union, Optional
from pathlib import Path
import logging
import json

from modules import get_available_colors

# Local Application Imports
from .helpers import (
    display_dataframe_from_lyrics,
    load_json_file,
    save_json_file,
    get_font_format,
)
from .handlers import handle_audio_processing
from modules import (
    fetch_and_save_lyrics,
    perform_lyric_enhancement,
    process_karaoke_subtitles,
    process_karaoke_video
)

# Initialize logger
logger = logging.getLogger(__name__)


# Callback Functions
def process_audio_callback(
    audio_file,
    override_meta,
    override_audio,
    override_transcribe,
    beam_size_input,
    best_of_input,
    patience_input,
    condition_toggle,
    compression_threshold_input,
    temperature_input,
    language_input,
    state_working_dir,
    state_lyrics_json,
    state_lyrics_display,
    cache_dir,
):
    """
    1) Runs the audio processing pipeline -> `raw_lyrics.json`
    2) Loads that JSON and sets up the states + left text box display.
    3) Updates the states: 
        `state_working_dir` -> working directory path, 
        `state_lyrics_json` -> `raw_lyrics.json`, 
        `state_lyrics_display` -> display text.
    """
    try:
        # If no audio file provided, return an error message
        if audio_file is None:
            return "Error: No audio file provided."

        # Handler: Audio processing pipeline
        # Returns: Path to raw_lyrics.json, and Path to working directory
        raw_lyrics_path, working_dir, title, artists = handle_audio_processing(
            audio_file,
            cache_dir,
            override_meta,
            override_audio,
            override_transcribe,
            beam_size_input,
            best_of_input,
            patience_input,
            condition_toggle,
            compression_threshold_input,
            temperature_input,
            language_input,
            file_name="raw_lyrics.json"
        )

        # Update State: working directory
        state_working_dir = working_dir

        # Load the `raw_lyrics.json`
        raw_lyrics_json = load_json_file(raw_lyrics_path)

        # Check if the file is empty or not found
        if not raw_lyrics_json:
            return "Error: No raw_lyrics.json found or empty."

        # Create display text
        display_text = display_dataframe_from_lyrics(raw_lyrics_path)

        # Update State: lyrics, lyrics to display
        state_lyrics_json = raw_lyrics_json
        state_lyrics_display = display_text
        state_artist_name = artists[0]
        state_song_name = title

        return (
            state_working_dir,
            state_lyrics_json,
            state_lyrics_display,
            state_artist_name,
            state_song_name
        )

    except Exception as e:
        logger.error(f"Error in process_audio_callback: {e}")
        return (None, None, f"Error: {e}")


def modify_lyrics_callback(
    override,
    state_working_dir,
    state_lyrics_json,
    state_lyrics_display
):
    """
    1) Calls AI lyric enhancement using reference_lyrics + raw_lyrics -> modifies time alignment
        Override (Default: True) will force re-run the AI model.
    2) Updates the states: 
        `state_lyrics_json` -> `modified_lyrics.json`, 
        `state_lyrics_display` -> modified display text.
    """
    try:
        # Check if working directory is set
        if not state_working_dir:
            return (state_lyrics_json, "Error: working dir not set")

        # Process our `raw_lyrics.json` and `reference_lyrics.json` to create
        # a `modified_lyrics.json` which is a corrected and aligned version
        # of the original transcribed `raw_lyrics.json`.
        # Returns: Path to the modified lyrics file
        modified_lyrics_path = perform_lyric_enhancement(
            output_path=state_working_dir,
            override=override,
            file_name="modified_lyrics.json"
        )

        # Load the `modified_lyrics.json`
        new_data = load_json_file(modified_lyrics_path)
        if not new_data:
            return (state_lyrics_json, "modified_lyrics.json is empty?")

        # Convert modified_lyrics format to a displayed text
        display_text = display_dataframe_from_lyrics(modified_lyrics_path)

        # Update States: lyrics, lyrics to display
        state_lyrics_json = new_data
        state_lyrics_display = display_text

        return (state_lyrics_json, state_lyrics_display)

    except Exception as e:
        logger.error(f"Error in modify_lyrics_callback: {e}")
        return (state_lyrics_json, f"Error: {e}")


def fetch_reference_lyrics_callback(
    override,
    state_working_dir,
    state_fetched_lyrics_json,
    state_fetched_lyrics_display
):
    """
    1) Runs or loads official lyrics from `reference_lyrics.json`.
        Override (Default: True) will force re-fetch the lyrics in every call.
    2) If not present, calls `fetch_and_save_lyrics(...)` to retrieve them.
    3) Updates the states:
        `state_fetched_lyrics_json` -> `reference_lyrics.json`,
        `state_fetched_lyrics_display` -> official lyrics to display.
    """
    try:
        # Check if working directory is set
        if not state_working_dir:
            return (state_fetched_lyrics_json, "Error: working dir not set")

        # Attempt to fetch reference lyrics + save
        # (this will skip if `reference_lyrics.json` already exists, unless override).
        fetch_and_save_lyrics(
            state_working_dir,
            override=override,
            file_name="reference_lyrics.json"
        )

        # Path to reference_lyrics.json
        ref_lyrics_path = Path(state_working_dir) / "reference_lyrics.json"

        # Load the `reference_lyrics.json` after fetching from online source
        lyrics_data = load_json_file(ref_lyrics_path)

        # Check if the file is empty or not found
        if not lyrics_data:
            return (None, "No official lyrics found or empty after fetch.")

        # If official lyrics are a list of strings (each item is one verse).
        # Join them into multiline string for editing
        if isinstance(lyrics_data, list):
            display_text = "\n".join(lyrics_data)
        else:
            # Else fallback if the JSON is not a list
            display_text = json.dumps(lyrics_data, indent=2)

        # Update States: fetched lyrics, fetched lyrics to display
        state_fetched_lyrics_json = lyrics_data
        state_fetched_lyrics_display = display_text

        return (state_fetched_lyrics_json, state_fetched_lyrics_display)

    except Exception as e:
        logger.error(f"Error in fetch_reference_lyrics_callback: {e}")
        return (state_fetched_lyrics_json, f"Error: {e}")


def save_fetched_lyrics_callback(
    fetched_lyrics_str,
    state_working_dir,
    state_fetched_lyrics_json,
    state_fetched_lyrics_display
):
    """
    1) Takes user-edited text from the right textbox, splits into lines, and overwrites reference_lyrics.json
    2) Updates the states:
        `state_fetched_lyrics_json` -> list of lines, 
        `state_fetched_lyrics_display` -> user-edited text.
    """
    try:
        # Check if working directory is set
        if not state_working_dir:
            return (state_fetched_lyrics_json, "Error: working dir not set")

        # Path to reference_lyrics.json
        ref_lyrics_path = Path(state_working_dir) / "reference_lyrics.json"

        # Turn the multiline string into a list of lines.
        # Each (str) line is a verse.
        new_lines = fetched_lyrics_str.splitlines()

        # Overwrite reference_lyrics.json with the new lines
        save_json_file(new_lines, ref_lyrics_path)

        # Update the states: fetched lyrics, fetched lyrics to display
        state_fetched_lyrics_json = new_lines
        state_fetched_lyrics_display = fetched_lyrics_str

        return (state_fetched_lyrics_json, state_fetched_lyrics_display)

    except Exception as e:
        logger.error(f"Error in save_fetched_lyrics_callback: {e}")
        return (state_fetched_lyrics_json, f"Error: {e}")


def save_metadata_callback(state_working_dir, artist_name, song_name):
    """
    Updates the metadata.json with the artist name and song name.
    """
    try:
        # Check if working directory is set
        if not state_working_dir:
            logger.error("Error: working dir not set")
            return

        # Update metadata.json with artist name and song name
        metadata_path = Path(state_working_dir) / "metadata.json"

        metadata = load_json_file(metadata_path)
        if not metadata:
            logger.error("Error loading metadata.json")
            return

        metadata["artists"][0] = artist_name
        metadata["title"] = song_name

        # Save the updated metadata
        save_json_file(metadata, metadata_path)
        logger.info(f"Metadata updated with artist: {artist_name}, song: {song_name}")
        return

    except Exception as e:
        logger.error(f"Error in save_metadata_callback: {e}")
        return


def ass_to_css_color(ass_color):
    hex_part = ass_color[4:]
    css_color = '#' + hex_part[4:6] + hex_part[2:4] + hex_part[0:2]
    return css_color


def generate_font_preview_callback(
    font: str,
    fontsize: int,
    primary_color: str,
    secondary_color: str,
    outline_color: str,
    outline_size: int,
    shadow_color: str,
    shadow_size: int,
    available_fonts: dict,
):
    """
    Generates the subtitle file and returns a formatted HTML preview of subtitles.
    """
    preview_text = "██ Karaoke Subtitle Font Preview"

    available_colors = get_available_colors()
    # Words to highlight (make the second half different color)
    split_index = len(preview_text) // 2
    highlighted_text = (
        f'<span style="color: {ass_to_css_color(available_colors[primary_color])};">'
        f'{preview_text[:split_index]}</span>'
        f'<span style="color: {ass_to_css_color(available_colors[secondary_color])};">'
        f'{preview_text[split_index:]}</span>'
    )
    font_format = get_font_format(available_fonts[font])

    # Generate preview HTML
    preview_html = f"""
    <style >
        @font-face {{
            font-family: {font};
            src: url('gradio_api/file={available_fonts[font]}') format('{font_format}');
        }}
    </style>
    <div style="
        font-family: {font};
        font-size: {fontsize}px;
        font-weight: bold;
        display: flex;
        justify-content: center;
        align-items: center;
        padding: 10px;
        background-color: black;
        text-align: center;
        color: {ass_to_css_color(available_colors[primary_color])};
        position: relative;
    ">
        <p style="
            position: relative;
            display: inline-block;
            color: {ass_to_css_color(available_colors[primary_color])};
            margin: 0;
            padding: 5px;
        ">
            <!-- Sharp Shadow -->
            <span style="
                position: absolute;
                left: {shadow_size}px;
                top: {shadow_size}px;
                color: {ass_to_css_color(available_colors[shadow_color])};
                z-index: -1;
                white-space: nowrap;
            ">
                {highlighted_text}
            </span>

            <!-- Correct Outline using Multi-Layered Shadows -->
            <span style="
                color: {ass_to_css_color(available_colors[primary_color])};
                text-shadow: 
                    -{outline_size}px -{outline_size}px 0 {ass_to_css_color(available_colors[outline_color])}, 
                     {outline_size}px -{outline_size}px 0 {ass_to_css_color(available_colors[outline_color])}, 
                    -{outline_size}px  {outline_size}px 0 {ass_to_css_color(available_colors[outline_color])}, 
                     {outline_size}px  {outline_size}px 0 {ass_to_css_color(available_colors[outline_color])};
            ">
                {highlighted_text}
            </span>
        </p>
    </div>
    """

    return preview_html


def generate_subtitles_and_video_callback(
    working_dir: str,

    # Subtitles parameters
    font: str,
    fontsize: int,
    primary_color: str,
    secondary_color: str,
    outline_color: str,
    outline_size: int,
    shadow_color: str,
    shadow_size: int,
    verses_before: int,
    verses_after: int,
    loader_threshold: float,

    # Video parameters
    effects_choice: Optional[Union[str, Path]],
    resolution: str,
    preset: str,
    crf: int,
    fps: int,
    bitrate: str,
    audio_bitrate: str,

    # Additional or override flags
    override_subs: bool,
    output_dir: str,
    effects_dir: str,
    fonts_dir: str
):
    """
    1) Generate Karaoke Subtitles (karaoke_subtitles.ass) 
       from (modified_lyrics.json or raw_lyrics.json).
    2) Generate Karaoke Video (karaoke_video.mp4).
    3) Return the final video path or a success message.
    """

    try:
        # ------------- Subtitles -------------
        screen_width, screen_height = map(int, resolution.split('x'))

        # Call your function (process_karaoke_subtitles) 
        # that produces "karaoke_subtitles.ass" in working_dir
        process_karaoke_subtitles(
            output_path=Path(working_dir),
            override=override_subs,
            file_name="karaoke_subtitles.ass",

            # Subtitle Settings
            font=font,
            fontsize=fontsize,
            primary_color=primary_color,
            secondary_color=secondary_color,
            outline_color=outline_color,
            outline_size=outline_size,
            shadow_color=shadow_color,
            shadow_size=shadow_size,
            screen_width=screen_width,
            screen_height=screen_height,
            verses_before=verses_before,
            verses_after=verses_after,
            loader_threshold=loader_threshold,
        )

        if effects_choice == "None":
            effect_video_path = None
        else:
            effect_video_path = Path(effects_dir) / effects_choice

        # ------------- Video -------------
        video_output_path = process_karaoke_video(
            working_dir=Path(working_dir),
            output_path=Path(output_dir),
            effect_path=effect_video_path,
            fonts_path=Path(fonts_dir),

            # Video Settings
            resolution=resolution,
            preset=preset,
            crf=crf,
            fps=fps,
            bitrate=bitrate,
            audio_bitrate=audio_bitrate,
        )

        return video_output_path

    except Exception as e:
        logger.error(f"Error generating subtitles or video: {e}")
        return f"Error: {e}"
