def load_lyrics_metadata(metadata_file):
    """
    Load the lyrics metadata and format it for editing in a table.
    """
    try:
        # Load the metadata from the JSON file
        with open(metadata_file, "r") as f:
            metadata = json.load(f)

        # Format metadata into rows for a DataFrame
        words = [
            (
                verse.get("verse_number"),  # Verse Number
                word.get("word_number"),   # Word Number
                word.get("word"),          # Word
                word.get("start"),         # Start Time
                word.get("end"),           # End Time
                word.get("probability")    # Probability
            )
            for verse in metadata
            for word in verse.get("words", [])
        ]
        return pd.DataFrame(words, columns=["Verse", "Word #", "Word", "Start", "End", "Probability"])
    
    except Exception as e:
        logger.error(f"Error loading metadata: {e}")
        return pd.DataFrame(columns=["Verse", "Word #", "Word", "Start", "End", "Probability"])


def save_modified_lyrics(metadata_file, modified_words):
    """
    Save modified lyrics back to the original metadata structure and file.
    """
    try:
        # Convert DataFrame to list of lists if needed
        if isinstance(modified_words, pd.DataFrame):
            modified_words = modified_words.values.tolist()

        # Load original metadata from JSON file
        with open(metadata_file, "r") as f:
            metadata = json.load(f)

        # Update words in the metadata structure
        word_index = 0
        for verse in metadata:
            for word in verse.get("words", []):
                if word_index < len(modified_words):
                    word["word"] = modified_words[word_index][2]  # Update the Word column (index 2)
                word_index += 1

        # Save updated metadata to JSON
        modified_file = Path(metadata_file).parent / "user_modified_lyrics.json"
        with open(modified_file, "w") as f:
            json.dump(metadata, f, indent=4)

        logger.info(f"Modified lyrics metadata saved at: {modified_file}")
        return str(modified_file)
    
    except Exception as e:
        logger.error(f"Error while saving modified metadata: {e}")
        return "Error saving modified metadata."
    

def expand_lyrics_metadata(metadata_file, modified_data):

    try:
        # Load the original metadata
        with open(metadata_file, "r") as f:
            metadata = json.load(f)

        # Update the words in the metadata with modified data
        word_index = 0
        for verse in metadata:
            for word in verse["words"]:
                if word_index < len(modified_data):
                    word["word"] = modified_data[word_index]["word"]
                word_index += 1

        # Save the modified metadata to a new file
        modified_file = Path(metadata_file).parent / "user_modified_lyrics.json"
        with open(modified_file, "w") as f:
            json.dump(metadata, f, indent=4)

        logger.info(f"Modified lyrics saved at: {modified_file}")
        return str(modified_file)
    except Exception as e:
        logger.error(f"Error expanding metadata: {e}")
        return "Error expanding metadata."
    
    def update_words(edited_text):
        """
        Update the state with edited words while preserving structure.
        """
        try:
            # Get the current words state
            current_words = state_words.value

            # Split the edited text back into individual verses
            edited_verses = edited_text.strip().split("\n\n")

            grouped_by_verse = {}
            for word in current_words:
                verse_number = word["verse_number"]
                if verse_number not in grouped_by_verse:
                    grouped_by_verse[verse_number] = []
                grouped_by_verse[verse_number].append(word)

            # Validate and update words
            for verse_number, edited_verse in enumerate(edited_verses, start=1):
                # Remove "Verse X:" prefix
                if edited_verse.startswith(f"Verse {verse_number}:"):
                    edited_verse = edited_verse[len(f"Verse {verse_number}: "):]

                original_words = grouped_by_verse[verse_number]
                edited_words = edited_verse.split()

                if len(original_words) != len(edited_words):
                    raise ValueError(
                        f"Word count mismatch in verse {verse_number}: "
                        f"expected {len(original_words)} words, got {len(edited_words)}."
                    )

                # Update the words in the state
                for i, word in enumerate(original_words):
                    word["word"] = edited_words[i]

            # Update the state
            state_words.value = current_words
            return "Verses updated successfully."
        except Exception as e:
            logger.error(f"Error updating words: {e}")
            return f"Error: {e}"
        
        # UPLOAD AUDIO FILE ====================================================
        # with gr.Row():
        #     gr.Markdown("### Upload an audio file")
        # with gr.Row():
        #     with gr.Column(scale=3):
        #         audio_input = gr.File(label="Upload Audio File", file_types=["audio"])
        #     with gr.Column(scale=1):
        #         override_checkbox = gr.Checkbox(
        #             label="Override Existing Files", value=False)
        # with gr.Row():
        # ARTIST AND SONG INFO ================================================
        # with gr.Row():
            # gr.Markdown("### Artist and Song Information")
        # INSPECT LYRICS OUTPUT ================================================
        # with gr.Row():
            # gr.Markdown("### Karaoke subttiles preview")
        # with gr.Row():
            # verses_textbox = gr.Textbox(
            #     label="Edit Verses",
            #     lines=10,
            #     placeholder="Processed verses will appear here...",
            #     interactive=True,
            # )
        # with gr.Row():
            # with gr.Column(scale=1):
                # refresh_button = gr.Button("Refresh", size="sm")
            # with gr.Column(scale=1):
                # magic_button = gr.Button("Magic Button", size="sm")


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
            # print(word_start)
            # print(word_end)
            # print(word_text)

            char_count = len(word_text)
            # print(char_count)

            segment_duration = (word_end - word_start) / char_count
            # print(segment_duration)

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


        filled_squares = f"{{\\c{loader_color}}}{'█' * i}{{\\c&HFF000000}}"  # 100% alpha for example
        unfilled_squares = '█' * (bar_length - i)
        loader_text = filled_squares + unfilled_squares