def format_time(seconds):
    """Convert time in seconds to ASS format (h:mm:ss.cs)."""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    seconds = seconds % 60
    return f"{hours}:{minutes:02}:{seconds:05.2f}"


def write_section(file, section_name, content):
    """Write a named section to the ASS file."""
    # Write the section name enclosed in brackets, e.g., [Script Info] or [V4+ Styles]
    file.write(f"[{section_name}]\n")
    
    # Write the content associated with this section
    file.write(content)
    
    # Add a blank line after the section for proper formatting
    file.write("\n")


def write_script_info(file, title="Karaoke Subtitles"):
    """Write the script information section."""
    # Create the content for the script info section, including the title and script type
    content = f"Title: {title}\nScriptType: v4.00+\nPlayDepth: 0\n"
    
    # Write the script info section using the `write_section` helper
    write_section(file, "Script Info", content)


def write_styles(file, font="Arial", fontsize=48, primary_color="&H00FFFFFF", secondary_color="&H0000FFFF",):
    """Write the styles section."""
    # Define the content for the styles section, including format and default style settings
    content = (
        "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, "
        "Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, "
        "Alignment, MarginL, MarginR, MarginV, Encoding\n"
        f"Style: Default,{font},{fontsize},{primary_color},{secondary_color},&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,3,0,5,0,0,0,1\n"
    )
    
    # Write the styles section using the `write_section` helper
    write_section(file, "V4+ Styles", content)


def write_events_header(file):
    """Write the header for the events section."""
    # Define the header for the events section, listing the format of dialogue events
    content = "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n"
    
    # Write the events header using the `write_section` helper
    write_section(file, "Events", content)


def write_dialogue(file, start, end, text, style="Default", margin_l=0, margin_r=0, margin_v=0):
    """Write a single dialogue event."""
    # Write a dialogue event in the ASS format with specified start and end times,
    # text content, and optional margins and style
    file.write(
        f"Dialogue: 0,{format_time(start)},{format_time(end)},{style},,{margin_l},{margin_r},{margin_v},,{text}\n"
    )


def write_title_event(file, title, title_duration, screen_height, fontsize=72):
    """Write the title event."""

    # Calculate vertical margin for the title, placing it at approximately 40% of the screen height
    margin_v = int(screen_height * 0.4)

    # Format the title text with the specified font size
    # The ASS tag '\\fs' sets the font size dynamically
    text = f"{{\\fs{fontsize}}}{title}"

    # Write the dialogue event for the title
    # The title is displayed from the start (0 seconds) to the specified `title_duration`
    write_dialogue(file, 0, title_duration, text, margin_v=margin_v)


def write_loader_event(file, loader_duration, screen_width, screen_height, loader_color="&H00FF0000", border_color="&HFFFFFF00", start_time=0.0):
    """Write a loader animation event."""
    # Vertical margin for the loader, positioned near the bottom of the screen
    margin_v = int(screen_height * 0.8)
    
    # Total number of segments to divide the loader into
    bar_length = 30

    # Duration of each segment in the loader animation
    segment_duration = loader_duration / bar_length

    # Write the static border event for the entire loader duration
    # This ensures a consistent border is displayed while the loader animates
    write_dialogue(
        file,
        start_time,
        start_time + loader_duration,
        f"{{\\c{border_color}}}",
        margin_v=margin_v
    )

    # Write progressive loader events
    for i in range(1, bar_length + 1):
        # Create the loader text with the current progress filled (`█`) and remaining space empty
        loader_text = f"|{'█' * i}{' ' * (bar_length - i)}|"

        # Calculate the start and end times for the current segment
        segment_start = start_time + (i - 1) * segment_duration
        segment_end = start_time + i * segment_duration

        # Write the dialogue for the current loader segment
        # Each segment progressively fills the loader bar
        write_dialogue(
            file,
            segment_start,
            segment_end,
            f"{{\\c{loader_color}}}{loader_text}",
            margin_v=margin_v
        )

# ! Note to self: Revisit to improve, refactor, and clean up
def write_lyrics_events(f, verses, primary_color="&H00FFFFFF", highlight_color="&H00FFFF00", loader_color="&H00FF0000", loader_threshold=10.0):
    """
    Write lyrics events with word-based timing, dynamic coloring during gaps, and loaders for long verse gaps.
    """
    num_verses = len(verses)

    for i in range(num_verses):
        # Determine previous, current, and next verses
        previous_verse = verses[i - 1] if i > 0 else None
        current_verse = verses[i]
        next_verse = verses[i + 1] if i + 1 < num_verses else None

        # Construct the previous verse (fully highlighted)
        previous_text = ""
        if previous_verse:
            previous_text = " ".join([f"{{\\c{highlight_color}}}{word['word']}{{\\c{primary_color}}}" for word in previous_verse["words"]])

        # Construct the next verse (not highlighted)
        next_text = ""
        if next_verse:
            next_text = " ".join([word["word"] for word in next_verse["words"]])

        # Handle the current verse (progressively highlighted)
        words = current_verse["words"]
        verse_start_time = words[0]["start"]
        verse_end_time = words[-1]["end"]

        for j, word in enumerate(words):
            word_start = word["start"]
            word_end = word["end"]
            word_text = word["word"]

            # Handle gaps between words in the current verse
            if j > 0:
                previous_word_end = words[j - 1]["end"]
                if word_start > previous_word_end:
                    # Dynamically color up to the most recently spoken point
                    progressive_text = " ".join(
                        f"{{\\c{highlight_color}}}{w['word']}{{\\c{primary_color}}}" if w["end"] <= previous_word_end else
                        f"{w['word']}"
                        for w in words
                    )
                    full_text = f"{previous_text}\\N\\N\\N\\N{progressive_text}\\N\\N\\N\\N{next_text}"
                    f.write(
                        f"Dialogue: 0,{format_time(previous_word_end)},{format_time(word_start)},Default,,0,0,0,,{full_text}\n"
                    )

            # Calculate letter-by-letter timing for the current word
            print(word_start)
            print(word_end)
            print(word_text)

            char_count = len(word_text)
            print(char_count)

            segment_duration = (word_end - word_start) / char_count
            print(segment_duration)

            for k in range(1, char_count + 1):
                # Progressively highlight the current word
                partially_highlighted = word_text[:k]
                remaining_text = word_text[k:]
                progressive_word = f"{{\\c{highlight_color}}}{partially_highlighted}{{\\c{primary_color}}}{remaining_text}"

                # Build the full current verse text with dynamically highlighted letters
                progressive_text = " ".join(
                    f"{{\\c{highlight_color}}}{w['word']}{{\\c{primary_color}}}" if w["start"] < word_start else
                    (progressive_word if w["word"] == word_text else w["word"])
                    for w in words
                )

                # Combine all three verses into a single Dialogue line
                full_text = ""
                if previous_text:
                    full_text += previous_text + r"\N\N\N\N"  # Add a newline for the previous verse
                full_text += progressive_text + r"\N\N\N\N"  # Add a newline for the current verse
                if next_text:
                    full_text += next_text  # Add the next verse

                # Write the combined Dialogue line for the current segment
                segment_start = word_start + (k - 1) * segment_duration
                segment_end = word_start + k * segment_duration
                f.write(f"Dialogue: 0,{format_time(segment_start)},{format_time(segment_end)},Default,,0,0,0,,{full_text}\n")

        # Ensure the full verse remains visible and dynamically colored until the last word's end time
        if words[-1]["end"] < verse_end_time:
            progressive_text = " ".join(
                f"{{\\c{highlight_color}}}{w['word']}{{\\c{primary_color}}}" if w["end"] <= words[-1]["end"] else
                f"{w['word']}"
                for w in words
            )
            full_text = ""
            if previous_text:
                full_text += previous_text + r"\N\N\N\N"
            full_text += progressive_text + r"\N\\N\N\N"
            if next_text:
                full_text += next_text
            f.write(f"Dialogue: 0,{format_time(words[-1]['end'])},{format_time(verse_end_time)},Default,,0,0,0,,{full_text}\n")

        # Handle gaps between current and next verse
        if next_verse:
            current_verse_end = words[-1]["end"]
            next_verse_start = next_verse["words"][0]["start"]
            verse_gap_duration = next_verse_start - current_verse_end

            if verse_gap_duration <= 5:
                # Keep the current state visible and ensure the current verse is fully colored
                fully_colored_current = " ".join(
                    f"{{\\c{highlight_color}}}{w['word']}{{\\c{primary_color}}}" for w in words
                )
                full_text = f"{previous_text}\\N\\N\\N\\N{fully_colored_current}\\N\\N\\N\\N{next_text}"
                f.write(
                    f"Dialogue: 0,{format_time(current_verse_end)},{format_time(next_verse_start)},Default,,0,0,0,,{full_text}\n"
                )
            elif 5 < verse_gap_duration <= 10:
                # Make the verses disappear
                full_text = ""
                f.write(
                    f"Dialogue: 0,{format_time(current_verse_end)},{format_time(next_verse_start)},Default,,0,0,0,,{full_text}\n"
                )
            elif verse_gap_duration > 10:
                # Display a loader for the duration of the gap
                bar_length = 30
                segment_duration = verse_gap_duration / bar_length

                for i in range(1, bar_length + 1):
                    loader_text = f"{{\\c{loader_color}}}|{'█' * i}{' ' * (bar_length - i)}|"
                    segment_start = current_verse_end + (i - 1) * segment_duration
                    segment_end = current_verse_end + i * segment_duration
                    f.write(
                        f"Dialogue: 0,{format_time(segment_start)},{format_time(segment_end)},Default,,0,0,0,,{loader_text}\n"
                    )


def extend_last_event(f, verses, audio_duration):
    """
    Extend the last line to the end of the audio.
    """
    if verses:
        # Retrieve the end time of the last verse
        last_verse_end = verses[-1]["end"]

        # Check if the end of the last verse is before the audio duration
        if last_verse_end < audio_duration:
            # Write a new dialogue event extending to the end of the audio
            f.write(f"Dialogue: 0,{format_time(last_verse_end)},{format_time(audio_duration)},Default,,0,0,0,,\n")


def create_ass_file(
    verses, 
    output_path, 
    audio_duration, 
    font="Arial", 
    fontsize=48, 
    primary_color="&H00FFFFFF",
    secondary_color="&H0000FFFF",
    title="Karaoke", 
    screen_width=1280, 
    screen_height=720
):
    """Generate an ASS subtitle file."""
    try:
        # Determine the start time of the first word in the verses
        first_word_start = verses[0]["words"][0]["start"]

        # Calculate the duration for the title display (25% of the pre-lyrics time)
        title_duration = first_word_start * 0.25

        # Calculate the duration for the loader animation (75% of the pre-lyrics time)
        loader_duration = first_word_start * 0.75

        # Open the output ASS file for writing
        with open(output_path, "w", encoding="utf-8") as file:
            # Write general script information such as title and script type
            write_script_info(file, title)

            # Write subtitle styles (e.g., font and alignment settings)
            write_styles(file, font, fontsize, primary_color, secondary_color)

            # Write the header for the events section
            write_events_header(file)

            # Write the title event if a title 
            write_title_event(file, title, title_duration, screen_height)

            # Write the loader animation event after the title
            write_loader_event(file, loader_duration, screen_width, screen_height, start_time=title_duration, loader_color=primary_color, border_color=primary_color)

            # Calculate the offset for the verses start times to follow the title and loader
            verses_start_time = title_duration + loader_duration

            # Adjust the start and end times of each verse
            for verse in verses:
                verse["start"] += verses_start_time
                verse["end"] += verses_start_time

            # Write the events for the lyrics with appropriate timing and formatting
            write_lyrics_events(file, verses, primary_color=primary_color, highlight_color=secondary_color, loader_color=secondary_color)

            # Extend the last subtitle event to cover any remaining audio duration
            extend_last_event(file, verses, audio_duration)

    except Exception as e:
        # Handle and re-raise any errors that occur during file generation
        raise RuntimeError(f"Failed to create ASS file: {e}") from e