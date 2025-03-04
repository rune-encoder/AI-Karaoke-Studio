# Standard Library Imports
from pathlib import Path
from typing import Union

# Local Application Imports
from .config import (get_available_colors, validate_and_get_color)

from .utilities import get_ass_rounded_rectangle

# Song title showing duration
# title_duration must be less then first_verse_start
title_duration = 4

# Duration between hiding old text and showing new text
gap_duration = 0.1


def format_time(seconds: float) -> str:
    """
    Convert a float time in seconds to an ASS-formatted timestamp:
        H:MM:SS.xx
    Example: 0:00:05.20
    """
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = seconds % 60
    return f"{hours}:{minutes:02}:{secs:05.2f}"


def write_section(file, section_name: str, content: str):
    """
    Write a named section to the .ass file:
        [Script Info]
        (content)

    Follow it with a blank line for proper formatting.
    """
    file.write(f"[{section_name}]\n")
    file.write(content)
    file.write("\n")


def write_script_info(
    file,
    title: str = "Karaoke Subtitles",
    screen_width: int = 1280,
    screen_height: int = 720
):
    """
    Writes [Script Info] section with resolution (PlayResX, PlayResY).
    """
    content = (
        f"Title: {title}\n"
        "ScriptType: v4.00+\n"
        f"PlayResX: {screen_width}\n"
        f"PlayResY: {screen_height}\n"
        "PlayDepth: 0\n"
    )
    write_section(file, "Script Info", content)


def write_style(
    style_name: str = "Default",
    font: str = "Lilita One Regular",
    fontsize: int = 60,
    primary_color: str = "&H0000A5FF",
    secondary_color: str = "&H00FFFFFF",
    outline_color: str = "&H00FF8080",
    outline_size: int = 3,
    shadow_color: str = "&H00FF8080",
    shadow_size: int = 0,
    margin_v: int = 0,
):
    return (
        f"Style: {style_name},{font},{fontsize},{primary_color},{secondary_color},"
        f"{outline_color},{shadow_color},"              # Use shadow_color instead of hardcoded black &H00000000
        "1,0,0,0,"                                      # Bold=1, Italic, Underline, StrikeOut
        "100,100,0,0,"                                  # ScaleX=100, ScaleY=100, Spacing, Angle
        f"1,{outline_size},{shadow_size},"              # BorderStyle=1, Outline=..., Shadow=...
        f"2,0,0,{margin_v},1\n"                         # Align=2, MarginV=..., Encoding=1
    )


def write_styles(
    file,
    font: str = "Lilita One Regular",
    fontsize: int = 60,
    primary_color: str = "&H0000A5FF",
    secondary_color: str = "&H00FFFFFF",
    outline_color: str = "&H00FF8080",
    outline_size: int = 3,
    shadow_color: str = "&H00FF8080",
    shadow_size: int = 0,
    screen_height: int = 0,
):
    """
    Write the [V4+ Styles] section with customizable font/color/outline/shadow.

    BorderStyle=1 => text has an outline rather than a box.
    """
    # You can choose to force BorderStyle=1 for outlines or 3 for "Opaque box" if you prefer.
    # Here we do BorderStyle=1 (outline).
    style_content = (
        "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, "
        "OutlineColour, BackColour, "
        "Bold, Italic, Underline, StrikeOut, "
        "ScaleX, ScaleY, Spacing, Angle, "
        "BorderStyle, Outline, Shadow, "
        "Alignment, MarginL, MarginR, MarginV, Encoding\n"
    )
    style_content += write_style(
        "Default",
        font,
        fontsize,
        primary_color,
        secondary_color,
        outline_color,
        outline_size,
        shadow_color,
        shadow_size,
        int(screen_height*0.4),
    )
    for (l_index, l_margin) in [(0, 0.8), (1, 0.6), (2, 0.4), (3, 0.2)]:
        style_content += write_style(
            f"Line{l_index}",
            font,
            fontsize,
            primary_color,
            secondary_color,
            outline_color,
            outline_size,
            shadow_color,
            shadow_size,
            int(screen_height*l_margin),
        )

    write_section(file, "V4+ Styles", style_content)


def write_events_header(file):
    """
    Write the [Events] header, defining the Dialogue format line.
    """
    content = "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n"
    write_section(file, "Events", content)


def write_dialogue(
    file,
    start: float,
    end: float,
    text: str,
    style: str = "Default",
    margin_l: int = 0,
    margin_r: int = 0,
    margin_v: int = 0
):
    """
    Write a single 'Dialogue' line with times, style, margins, and text.
    Example:
        Dialogue: 0,0:00:01.20,0:00:03.00,Default,,0,0,0,,Some text
    """
    file.write(
        f"Dialogue: 0,{format_time(start)},{format_time(end)},{style},,{margin_l},{margin_r},{margin_v},,{text}\n"
    )


def write_title_event(
    file,
    title: str,
    title_duration: float,
    screen_height: int,
    fontsize: int,
):
    """
    Display a large title from t=0 to t=title_duration, vertically about 40% down the screen.
    """
    margin_v = int(screen_height * 0.4)
    text = f"{{\\fs{fontsize}}}{title}"
    write_dialogue(file, 0, title_duration, text, margin_v=margin_v)


def write_loader_event(
    file,
    start_time: float,
    loader_duration: float,
    screen_width: int,
    screen_height: int,
    loader_color: str = "&H00FF0000",
    border_color: str = "&HFFFFFF00",
):
    """
    Display a progressive loader for 'loader_duration' seconds. 
    """
    margin_v = screen_height // 2
    bar_length = 30
    loader_text = '█'*bar_length

    write_dialogue(file, start_time, start_time + loader_duration, loader_text, margin_v=margin_v)


def extend_last_event(
    file,
    verses,
    audio_duration
):
    """
    Extend the final subtitle to the end of the audio if leftover time exists.
    """
    if not verses:
        return

    last_verse_end = verses[-1]["end"]
    if last_verse_end < audio_duration:
        write_dialogue(file, last_verse_end, audio_duration, '')



def write_lyrics_events(
    file,
    verses: list,
    screen_width: int,
    screen_height: int,
    primary_color: str = "&H0000A5FF",
    highlight_color: str = "&H0000A5FF",
    loader_color: str = "&H00FF0000",
    loader_threshold: float = 5.0,
    verses_before: int = 1,
    verses_after: int = 1,
    fontsize: int = 60,
):
    """
    Write karaoke-style dialogues with a 'window' of verses showing.
    If the gap to the next verse > loader_threshold, display a loader.
    """

    # Set line index, from upper [0] to bottom [3]
    for (v_index, verse) in enumerate(verses):
        verse["line"] = v_index % 4

    # Alternating upper and bottom verses
    line1_end = line3_end = verses[-1]["end"]
    for verse in reversed(verses):
        match verse["line"]:
            case 0:
                verse["end"] = line1_end
            case 1:
                verse["end"] += gap_duration
                line1_end = verse["end"]
            case 2:
                verse["end"] = line3_end
            case 3:
                verse["end"] += gap_duration
                line3_end = verse["end"]

    line1_end = line3_end =  title_duration + gap_duration
    for verse in verses:
        match verse["line"]:
            case 0:
                verse["start"] = line1_end
            case 1:
                verse["start"] = line1_end
                line1_end = verse["end"] + gap_duration
            case 2:
                verse["start"] = line3_end
            case 3:
                verse["start"] = line3_end
                line3_end = verse["end"] + gap_duration

    prev_verse_end = verses[0]["start"]
    for verse in verses:
        # Visible loader between last word of previous verse and first word of next verse
        word_duration = int((verse["words"][0]["start"] - prev_verse_end)*100)
        if word_duration > 0:
            len_word = 7 if word_duration > 2800 else word_duration // 400
            # If len_word = 0 then it will be invisible short loader
            verse["words"].insert(0, {
                "word": get_ass_rounded_rectangle(fontsize*len_word, fontsize*2//3, fontsize//5),
                "start": prev_verse_end,
                "end": verse["words"][0]["start"]
            })
        # Invisible loader which compensates for the length of all previous verses on the page
        word_duration = int((prev_verse_end - verse["start"])*100)
        if word_duration > 0:
            verse["words"].insert(0, {
                "word": '',
                "start": verse["start"],
                "end": prev_verse_end
            })
        prev_verse_end = verse["words"][-1]["end"]

    # Apply karaoke effect
    for verse in verses:
        for word in verse["words"]:
            word_duration = int((word["end"] - word["start"])*100)
            word["word"] = f"{{\\kf{word_duration}}}{word['word']}"

    # Write formatted verses with loaders and karaoke effects
    for verse in verses:
        words = [word["word"] for word in verse["words"]]
        write_dialogue(file, verse["start"], verse["end"], ' '.join(words), style=f"Line{verse['line']}")


def create_ass_file(
    verses_data: list,
    output_path: Union[str, Path],
    audio_duration: float,
    font: str = "Lilita One Regular",
    fontsize: int = 60,
    primary_color: str = "&H0000A5FF",    # White in ASS color
    secondary_color: str = "&H00FFFFFF",  # Yellow or other highlight color
    outline_color: str = "&H00FF8080",    # Outline color (black)
    outline_size: int = 3,
    shadow_color: str = "&H00FF8080",
    shadow_size: int = 0,
    title: str = "Karaoke",
    screen_width: int = 1280,
    screen_height: int = 720,
    verses_before: int = 1,
    verses_after: int = 1,
    loader_threshold: int = 5.0,
):
    """
    Generate a complete .ass subtitle file with:
      - Title event (e.g. Karaoke)
      - Loader event (before first verse)
      - Timed, letter-by-letter karaoke highlighting
      - Optional bridging loader if gaps > 5s
      - Extended last event to audio end
    """
    try:
        available_colors = get_available_colors()
        primary_color = validate_and_get_color(primary_color, "&H0000A5FF", available_colors)
        secondary_color = validate_and_get_color(secondary_color, "&H00FFFFFF", available_colors)
        outline_color = validate_and_get_color(outline_color, "&H00FF8080", available_colors)
        shadow_color = validate_and_get_color(shadow_color, "&H00FF8080", available_colors)

        with open(output_path, "w", encoding="utf-8") as file:
            # [Script Info]
            write_script_info(
                file,
                title=title,
                screen_width=screen_width,
                screen_height=screen_height
            )

            # [V4+ Styles]
            write_styles(
                file,
                font=font,
                fontsize=fontsize,
                primary_color=primary_color,
                secondary_color=secondary_color,
                outline_color=outline_color,
                outline_size=outline_size,
                shadow_color=shadow_color,
                shadow_size=shadow_size,
                screen_height=screen_height
            )

            # [Events]
            write_events_header(file)

            # [Title Event]
            write_title_event(file, title, title_duration, screen_height, fontsize=fontsize+12)

            # Write main lyrics
            write_lyrics_events(
                file,
                verses_data,
                screen_width,
                screen_height,
                primary_color=primary_color,
                highlight_color=secondary_color,
                loader_color=secondary_color,
                loader_threshold=loader_threshold,
                verses_before=verses_before,
                verses_after=verses_after,
                fontsize=fontsize,
            )

            # Extend last event if there's leftover audio
            extend_last_event(file, verses_data, audio_duration)

    except Exception as e:
        raise RuntimeError(f"Failed to create ASS file: {e}") from e
