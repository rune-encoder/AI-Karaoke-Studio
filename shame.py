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
