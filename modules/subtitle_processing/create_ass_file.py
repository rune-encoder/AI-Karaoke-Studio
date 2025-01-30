# Standard Library Imports
from pathlib import Path
from typing import Union

# Local Application Imports
from .config import (get_available_colors, validate_and_get_color)

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


def write_styles(
    file,
    font: str = "Arial",
    fontsize: int = 48,
    primary_color: str = "&H00FFFFFF",
    secondary_color: str = "&H0000FFFF",
    outline_color: str = "&H00000000",
    outline_size: int = 2,
    shadow_color: str = "&H00000000",
    shadow_size: int = 0,
):
    """
    Write the [V4+ Styles] section with customizable font/color/outline/shadow.

    BorderStyle=1 => text has an outline rather than a box. 
    """
    # You can choose to force BorderStyle=1 for outlines or 3 for "Opaque box" if you prefer.
    # Here we do BorderStyle=1 (outline).
    style_content = (
        "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, "
        "OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, "
        "ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, "
        "Alignment, MarginL, MarginR, MarginV, Encoding\n"
        f"Style: Default,{font},{fontsize},{primary_color},{secondary_color},"
        # BackColour: transparent
        f"{outline_color},{shadow_color},"              # Use shadow_color instead of hardcoded black &H00000000
        "0,0,0,0,"                                      # Bold, Italic, Underline, StrikeOut
        "100,100,0,0,"                                  # ScaleX, ScaleY, Spacing, Angle
        # BorderStyle=1, Outline=..., Shadow=..., Align=5
        f"1,{outline_size},{shadow_size},5,0,0,0,1\n"
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
        f"Dialogue: 0,{format_time(start)},{format_time(end)},{style},,"
        f"{margin_l},{margin_r},{margin_v},,{text}\n"
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
    loader_duration: float,
    screen_width: int,
    screen_height: int,
    loader_color: str = "&H00FF0000",
    border_color: str = "&HFFFFFF00",
    start_time: float = 0.0
):
    """
    Display a progressive loader for 'loader_duration' seconds. 
    Each segment is ~ (loader_duration / bar_length).
    """
    margin_v = screen_height // 2
    bar_length = 30
    segment_dur = loader_duration / bar_length

    for i in range(1, bar_length + 1):
        # Each iteration: fill i squares, unfilled (bar_length - i).
        # We color the unfilled squares with alpha=0 (invisible).
        # filled = f"{{\\c{loader_color}}}|{'█'*i}"
        # unfilled = f"{{\\c&H00000000}}{'█'*(bar_length-i)}"
        # trailing = f"{{\\c{loader_color}}}|"

        filled = f"{{\\c{loader_color}}}{'█'*i}"
        unfilled = f"{{\\c&H80000000}}{'█'*(bar_length-i)}"

        loader_text = filled + unfilled

        seg_start = start_time + (i - 1) * segment_dur
        seg_end = start_time + i * segment_dur
        write_dialogue(file, seg_start, seg_end,loader_text, margin_v=margin_v)


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
        file.write(
            f"Dialogue: 0,{format_time(last_verse_end)},"
            f"{format_time(audio_duration)},Default,,0,0,0,,\n"
        )


def write_lyrics_events(
    file,
    verses,
    primary_color: str = "&H00FFFFFF",
    highlight_color: str = "&H0000FFFF",
    loader_color: str = "&H00FF0000",
    loader_threshold: float = 5.0,
    verses_before: int = 1,
    verses_after: int = 1,
):
    """
    Write karaoke-style dialogues with a 'window' of verses showing:
      - 'verses_before' fully highlighted (previous verses)
      - 'verses_after' unhighlighted (upcoming verses)
      - The current verse is letter-by-letter highlighted

    If the gap to the next verse > loader_threshold, display a loader.
    """
    num_verses = len(verses)

    def build_fully_highlighted_text(verse):
        return " ".join(
            f"{{\\c{highlight_color}}}{w['word']}{{\\c{primary_color}}}"
            for w in verse["words"]
        )

    def build_unhighlighted_text(verse):
        return " ".join(w["word"] for w in verse["words"])

    for i in range(num_verses):
        # --- Collect previous verses (fully highlighted) ---
        prev_texts = []
        start_prev = max(0, i - verses_before)
        for p in range(start_prev, i):
            prev_texts.append(build_fully_highlighted_text(verses[p]))

        # --- Current verse (letter-by-letter highlight) ---
        curr_verse = verses[i]
        words = curr_verse["words"]
        verse_start_time = words[0]["start"]
        verse_end_time   = words[-1]["end"]

        # --- Collect next verses (unhighlighted) ---
        upcoming_texts = []
        end_next = min(num_verses, i + 1 + verses_after)
        for n in range(i + 1, end_next):
            upcoming_texts.append(build_unhighlighted_text(verses[n]))

        # --- Letter-by-letter highlighting logic ---
        for j, word in enumerate(words):
            word_start = word["start"]
            word_end   = word["end"]
            word_text  = word["word"]

            # If there's a gap since the previous word, fill it
            if j > 0:
                prev_end = words[j - 1]["end"]
                # Up to 'prev_end' => highlight everything spoken so far
                if word_start > prev_end:
                    so_far = []
                    for w2 in words:
                        if w2["end"] <= prev_end:
                            so_far.append(f"{{\\c{highlight_color}}}{w2['word']}{{\\c{primary_color}}}")
                        else:
                            so_far.append(w2["word"])

                    # Combine: previous verses + so_far + upcoming
                    blocks = prev_texts + [" ".join(so_far)] + upcoming_texts
                    full_text = r"\N\N\N\N".join(blocks)
                    file.write(
                        f"Dialogue: 0,{format_time(prev_end)},{format_time(word_start)},Default,,0,0,0,,{full_text}\n"
                    )

            # Break word_text into letters
            char_count = len(word_text)
            if char_count == 0:
                continue

            seg_dur = (word_end - word_start) / char_count
            for k in range(1, char_count + 1):
                # partial highlight up to letter k
                highlighted_part = word_text[:k]
                remaining_part   = word_text[k:]
                partial_word     = f"{{\\c{highlight_color}}}{highlighted_part}{{\\c{primary_color}}}{remaining_part}"

                # Build progressive text for entire verse
                progressive = []
                for w2 in words:
                    if w2["start"] < word_start:
                        # Fully highlight words before the one we're animating
                        progressive.append(f"{{\\c{highlight_color}}}{w2['word']}{{\\c{primary_color}}}")
                    elif w2["word"] == word_text:
                        progressive.append(partial_word)
                    else:
                        progressive.append(w2["word"])

                # Combine: prev verses + current partial + upcoming
                blocks = prev_texts + [" ".join(progressive)] + upcoming_texts
                full_text = r"\N\N\N\N".join(blocks)

                seg_start = word_start + (k - 1) * seg_dur
                seg_end   = word_start + k * seg_dur
                file.write(
                    f"Dialogue: 0,{format_time(seg_start)},{format_time(seg_end)},Default,,0,0,0,,{full_text}\n"
                )

        # If leftover from last word to verse_end_time, fill it
        if words[-1]["end"] < verse_end_time:
            last_end = words[-1]["end"]
            post_text = []
            for w2 in words:
                if w2["end"] <= last_end:
                    post_text.append(f"{{\\c{highlight_color}}}{w2['word']}{{\\c{primary_color}}}")
                else:
                    post_text.append(w2["word"])

            blocks = prev_texts + [" ".join(post_text)] + upcoming_texts
            full_text = r"\N\N\N\N".join(blocks)
            file.write(
                f"Dialogue: 0,{format_time(last_end)},{format_time(verse_end_time)},Default,,0,0,0,,{full_text}\n"
            )

        # --- Check gap between current verse and next verse ---
        if i + 1 < num_verses:
            next_start    = verses[i + 1]["words"][0]["start"]
            curr_verse_end = words[-1]["end"]
            gap_duration   = next_start - curr_verse_end

            if gap_duration <= loader_threshold:
                # keep the fully-colored current verse on screen
                fully_colored_current = " ".join(
                    f"{{\\c{highlight_color}}}{w['word']}{{\\c{primary_color}}}" for w in words
                )
                blocks = prev_texts + [fully_colored_current] + upcoming_texts
                full_text = r"\N\N\N\N".join(blocks)
                file.write(
                    f"Dialogue: 0,{format_time(curr_verse_end)},{format_time(next_start)},Default,,0,0,0,,{full_text}\n"
                )
            else:
                # Show a loader if gap > loader_threshold
                bar_length = 30
                gap_seg_dur = gap_duration / bar_length

                for seg_i in range(1, bar_length + 1):
                    filled = f"{{\\c{loader_color}}}|{'█' * seg_i}"
                    unfilled = f"{{\\c&H00000000}}{'█' * (bar_length - seg_i)}"
                    trailing = f"{{\\c{loader_color}}}|"
                    loader_text = filled + unfilled + trailing

                    seg_start = curr_verse_end + (seg_i - 1) * gap_seg_dur
                    seg_end   = curr_verse_end + seg_i * gap_seg_dur
                    file.write(
                        f"Dialogue: 0,{format_time(seg_start)},{format_time(seg_end)},Default,,0,0,0,,{loader_text}\n"
                    )

def create_ass_file(
    verses_data: list,
    output_path: Union[str, Path],
    audio_duration: float,
    font: str = "Arial",
    fontsize: int = 24,
    primary_color: str = "&H00FFFFFF",    # White in ASS color
    secondary_color: str = "&H0000FFFF",  # Yellow or other highlight color
    outline_color: str = "&H00000000",    # Outline color (black)
    outline_size: int = 2,
    shadow_color: str = "&H00000000",
    shadow_size: int = 0,
    title: str = "Karaoke",
    screen_width: int = 1280,
    screen_height: int = 720,
    verses_before: int = 1,
    verses_after: int = 1,
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
        primary_color = validate_and_get_color(primary_color, "&H00FFFFFF", available_colors)
        secondary_color = validate_and_get_color(secondary_color, "&H0000FFFF", available_colors)
        outline_color = validate_and_get_color(outline_color, "&H00000000", available_colors)
        shadow_color = validate_and_get_color(shadow_color, "&H00000000", available_colors)

        # Time before first verse => split into title and loader durations
        first_word_start = verses_data[0]["words"][0]["start"]
        title_duration   = first_word_start * 0.25
        loader_duration  = first_word_start * 0.75

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
                shadow_size=shadow_size
            )

            # [Events]
            write_events_header(file)

            # [Title Event]
            write_title_event(file, title, title_duration, screen_height, fontsize=fontsize+12)

            # [Loader Event]
            write_loader_event(
                file,
                loader_duration,
                screen_width,
                screen_height,
                loader_color=secondary_color,    # Fill...
                border_color=primary_color,      # Border...
                start_time=title_duration,
            )

            # Shift verse times after loader
            verses_start_time = title_duration + loader_duration
            for verse in verses_data:
                verse["start"] += verses_start_time
                verse["end"]   += verses_start_time

            # Write main lyrics
            write_lyrics_events(
                file,
                verses_data,
                primary_color=primary_color,
                highlight_color=secondary_color,
                loader_color=secondary_color,
                loader_threshold=5.0,    # gap > 5s => show loader
                verses_before=verses_before,
                verses_after=verses_after
            )
            
            # Extend last event if there's leftover audio
            extend_last_event(file, verses_data, audio_duration)

    except Exception as e:
        raise RuntimeError(f"Failed to create ASS file: {e}") from e
