# Standard Library Imports
import gradio as gr

# Local Application Imports
from .callbacks import (
    process_audio_callback,
    fetch_reference_lyrics_callback,
    save_fetched_lyrics_callback,
    modify_lyrics_callback,
)


def process_placeholder_callback(
    raw_lyrics_box_text,
    fetched_lyrics_box_text
):
    """
    A placeholder function for the 'Process' button. 
    Just returns a message or some combined text for now.
    """
    msg = (
        "Placeholder process button.\n\n"
        "Left side:\n" + str(raw_lyrics_box_text) + "\n\n"
        "Right side:\n" + str(fetched_lyrics_box_text)
    )
    return msg


# Main App Interface
def main_app(cache_dir, output_dir):
    with gr.Blocks() as app:

        gr.Markdown("# 🎤 Karaoke Generator")

        # States
        state_working_dir = gr.State(value="")
        state_lyrics_json = gr.State(value=None)
        state_lyrics_display = gr.State(value="")
        state_fetched_lyrics_json = gr.State(value=None)
        state_fetched_lyrics_display = gr.State(value="")

        # ---------------------------- SECTION 1 ----------------------------
        gr.Markdown("# _____")
        with gr.Row():
            with gr.Column():
                audio_input = gr.File(
                    label="Upload Audio",
                    file_types=["audio"],
                    type="filepath"
                )

                with gr.Accordion("Advanced Options", open=False):
                    override_audio_processing = gr.Checkbox(
                        label="Override?",
                        value=False,
                    )

                process_audio_button = gr.Button(
                    "Process Audio",
                    variant="primary"
                )

        # ---------------------------- SECTION 2 ----------------------------
        gr.Markdown("# _____")
        with gr.Row():
            with gr.Column():
                fetched_lyrics_box = gr.Textbox(
                    label="Reference Lyrics (Editable)",
                    lines=20,
                    interactive=True,
                )
                with gr.Row():
                    fetch_button = gr.Button("🌐 Fetch Reference Lyrics")
                    save_button = gr.Button("💾 Update Reference Lyrics")

            with gr.Column():
                raw_lyrics_box = gr.Dataframe(
                    headers=["Processed Lyrics (Used for Karaoke)"],
                    label="Processed Lyrics (Used for Karaoke)",
                    datatype=["str"],
                    interactive=False,
                    show_label=False,
                    max_height=465,
                )
                with gr.Row():
                    modify_button = gr.Button(
                        "🪄 Modify with AI",
                        variant="primary",
                    )

        with gr.Row():
            with gr.Accordion("Advanced Options", open=False):
                override_fetch_lyrics = gr.Checkbox(
                    label="Re-fetch lyrics from API? (Overrides 'Fetch Reference Lyrics' button)",
                    value=False,
                )
                override_modify_lyrics = gr.Checkbox(
                    label="Re-send lyrics for alignment? (Overrides 'Modify with AI' button)",
                    value=False,
                )
        # ---------------------------- SECTION 3 ----------------------------
        gr.Markdown("# _____")
        with gr.Row():
            process2_button = gr.Button(
                "Process (Placeholder)",
                variant="primary",
            )

        process_output = gr.Textbox(
            label="Process Output",
            lines=6,
            interactive=False
        )

        # ----------------------- Wire up the callbacks -----------------------

        # (Primary) Process Audio Button
        # Updates States: working directory, lyrics data, and lyrics to display
        # Displays the updated `state_lyrics_display` in the `raw_lyrics_box`
        process_audio_button.click(
            # `.click()` event: Update the status of our states
            fn=process_audio_callback,
            inputs=[
                audio_input,
                override_audio_processing,
                state_working_dir,
                state_lyrics_json,
                state_lyrics_display,
                gr.State(cache_dir),  # Hidden state: cache_dir
            ],
            outputs=[
                state_working_dir,
                state_lyrics_json,
                state_lyrics_display
            ]
        ).then(
            # `.then()` event: After states are updated, display them in display box
            fn=lambda disp: disp,
            inputs=state_lyrics_display,
            outputs=raw_lyrics_box
        )

        # (Secondary) 🌐 Fetch Reference Lyrics Button
        # Updates States: fetched lyrics, fetched lyrics to display
        # Displays the updated `state_fetched_lyrics_display` in the `fetched_lyrics_box`
        fetch_button.click(
            fn=fetch_reference_lyrics_callback,
            inputs=[
                override_fetch_lyrics,
                state_working_dir,
                state_fetched_lyrics_json,
                state_fetched_lyrics_display
            ],
            outputs=[
                state_fetched_lyrics_json,
                state_fetched_lyrics_display
            ]
        ).then(
            fn=lambda disp: disp,
            inputs=state_fetched_lyrics_display,
            outputs=fetched_lyrics_box
        )

        # (Secondary) 💾 Update Reference Lyrics Button
        # Updates States: fetched lyrics, fetched lyrics to display
        # Displays the updated `state_fetched_lyrics_display` in the `fetched_lyrics_box`
        save_button.click(
            fn=save_fetched_lyrics_callback,
            inputs=[
                fetched_lyrics_box,
                state_working_dir,
                state_fetched_lyrics_json,
                state_fetched_lyrics_display
            ],
            outputs=[
                state_fetched_lyrics_json,
                state_fetched_lyrics_display
            ]
        )

        # (Secondary) 🪄 Modify with AI Button
        # Updates States: lyrics, lyrics to display
        # Displays the updated `state_lyrics_display` in the `lyrics_box`
        modify_button.click(
            fn=modify_lyrics_callback,
            inputs=[
                override_modify_lyrics,
                state_working_dir,
                state_lyrics_json,
                state_lyrics_display
            ],
            outputs=[
                state_lyrics_json,
                state_lyrics_display
            ]
        ).then(
            fn=lambda disp: disp,
            inputs=state_lyrics_display,
            outputs=raw_lyrics_box
        )

        # Process (placeholder) -> merges raw + fetched text
        process2_button.click(
            fn=process_placeholder_callback,
            inputs=[raw_lyrics_box, fetched_lyrics_box],
            outputs=process_output
        )

    return app
