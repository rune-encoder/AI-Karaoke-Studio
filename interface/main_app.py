# Standard Library Imports
import gradio as gr

# Local Application Imports
from .callbacks import (
    process_audio_callback,
    fetch_reference_lyrics_callback,
    save_fetched_lyrics_callback,
    modify_lyrics_callback,
    generate_font_preview_callback,
    generate_subtitles_and_video_callback,
    save_metadata_callback,
)

from .helpers import (
    check_modify_ai_availability,
    check_generate_karaoke_availability,
    get_effect_video_list,
    get_available_languages,
)

from modules import (
    get_available_colors,
    get_font_list,
)

import pandas as pd

# Main App Interface
def main_app(cache_dir, fonts_dir, output_dir, project_root):
    gr.set_static_paths(fonts_dir)
    with gr.Blocks(theme='shivi/calm_seafoam') as app:
        effects_dir = project_root / "effects"

        # Get available fonts and colors for subtitles
        available_fonts = get_font_list(fonts_dir)
        available_colors = get_available_colors()
        available_effects = ["None"] + get_effect_video_list(effects_dir)
        available_langs = ["Auto Detect"] + sorted(get_available_languages().keys())

        ##############################################################################
        #                               APP STATES
        ##############################################################################
        state_working_dir = gr.State(value="")
        state_lyrics_json = gr.State(value=None)
        state_lyrics_display = gr.State(value="")
        state_fetched_lyrics_json = gr.State(value=None)
        state_fetched_lyrics_display = gr.State(value="")
        state_artist_name = gr.State(value="")
        state_song_name = gr.State(value="")

        ##############################################################################
        #                                APP HEADER
        ##############################################################################
        gr.HTML("<hr>")
        gr.Markdown("# 🎤 Karaoke Generator")
        gr.HTML("<hr>")

        ##############################################################################
        #                    SECTION 1: AUDIO PROCESSING
        ##############################################################################
        gr.Markdown("## 1) Audio Processing and Vocals Transcription")
        gr.Markdown("### _Upload an audio file to begin audio processing and vocals transcription._")
        with gr.Row():
            with gr.Column():
                audio_input = gr.Audio(
                    label="Upload Audio",
                    type="filepath",
                    sources="upload",
                )

                # --- ADVANCED SETTINGS ---
                with gr.Accordion("Developer Settings", open=False):
                    force_meta_fetch = gr.Checkbox(
                        label="Re-run Metadata Fetching?",
                        value=False,
                        info="Forces re-running metadata fetching (artist, song name, etc.)."
                    )
                    force_audio_processing = gr.Checkbox(
                        label="Re-run Audio Processing?",
                        value=False,
                        info="Forces re-running the audio processing (stem separation, stem merging, etc.)."
                    )
                    force_transcription = gr.Checkbox(
                        label="Re-run Vocals Transcription?",
                        value=False,
                        info="Forces re-running the audio transcription (vocals transcription, etc.)."
                    )

                with gr.Accordion("Transcription Accuracy Settings (Advanced)", open=False):
                    with gr.Row():
                        with gr.Column():
                            beam_size_input = gr.Slider(
                                minimum=1, maximum=20, step=1, value=15,
                                label="Beam Size (Higher = More Accuracy, Slower)"
                            )
                            best_of_input = gr.Slider(
                                minimum=1, maximum=10, step=1, value=5,
                                label="Best Of (Higher = More Alternatives Evaluated)"
                            )
                        with gr.Column():
                            patience_input = gr.Number(
                                value=3.0, label="Patience (Extra Time for Segments)"
                            )
                            condition_toggle = gr.Checkbox(
                                label="Condition on Previous Text",
                                value=False,
                                info="For karaoke, set to False to help capture repeated words."
                            )
                        with gr.Column():
                            compression_threshold_input = gr.Slider(
                                minimum=1.0, maximum=2.0, step=0.1, value=1.3,
                                label="Compression Ratio Threshold"
                            )
                            temperature_input = gr.Slider(
                                minimum=0.0, maximum=1.0, step=0.1, value=0.0,
                                label="Temperature (0 = Deterministic)"
                            )
                    with gr.Row():
                        language_input = gr.Dropdown(
                            choices=available_langs,
                            label="Transcription Language", 
                            value="Auto Detect",
                            info="Select a language if auto-detection is not reliable; otherwise, choose 'Auto Detect'."
                        )

                process_audio_button = gr.Button(
                    "Process Audio",
                    variant="primary"
                )
        gr.HTML("<hr>")

        ##############################################################################
        #                    SECTION 2: LYRIC ADJUSTMENTS
        ##############################################################################
        gr.Markdown("## 2) Lyric Correction and Re-Alignment.")
        gr.Markdown("### _Correct the generated and timed vocal transcription using a reliable lyrics source as a reference._")
        with gr.Row():
            with gr.Column():
                artist_name_input = gr.Textbox(
                    label="Artist Name",
                    lines=1,
                    interactive=True,
                )
            with gr.Column():
                song_name_input = gr.Textbox(
                    label="Song Name",
                    lines=1,
                    interactive=True,
                )
        save_metadata_button = gr.Button("💾 Save Artist and Song Name")
        with gr.Row():
            with gr.Column():
                gr.Markdown("##### Lyrics to reference for correction and re-alignment of vocals transcription.")
                gr.Markdown("""
                - In this section you can source the reference lyrics from an API or input them yourself.
                - The refrence lyrics will be used by the AI to correct and re-align the original lyrics.
                - To fetch the lyrics press the `Fetch Reference Lyrics` button.
                - If you are unable to fetch, the fetched lyrics are incorrect, or want to use your own lyrics, paste 
                them into the text-box. Ensure there are no empty lines between verses. Then save by pressing the
                `Update Reference Lyrics` button.
                """)
                fetched_lyrics_box = gr.Textbox(
                    label="Reference Lyrics (Editable)",
                    lines=20,
                    interactive=True,
                )
                with gr.Row():
                    fetch_button = gr.Button("🌐 Fetch Reference Lyrics")
                    save_button = gr.Button("💾 Update Reference Lyrics")

            with gr.Column():
                gr.Markdown("##### Formatted lyrics used to generate Karaoke Subtitles with word timing.")
                gr.Markdown("""
                - This section will display the raw transcription or corrected re-aligned transcription.
                - To correct and re-align the raw transcription press on the `Modify with AI` button.
                - Note that before you can select this, you need to have the refence lyrics (on the left) saved.
                - The system will then send the raw transcription and the reference lyrics to AI for correction and re-alignment.
                """)
                raw_lyrics_box = gr.Dataframe(
                    value=pd.DataFrame({
                        "Processed Lyrics (Used for Karaoke)": ["" for _ in range(12)]
                    }),
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
                        interactive=False
                    )

        # --- ADVANCED SETTINGS ---
        with gr.Row():
            with gr.Accordion("Developer Settings", open=False):
                force_refetch_lyrics = gr.Checkbox(
                    label="Re-Fetch Reference Lyrics?",
                    value=False,
                    info="Ignores the local `reference_lyrics.json` and fetches new lyrics from the API."
                )
                force_ai_modification = gr.Checkbox(
                    label="Re-run AI Lyric Modification?",
                    value=False,
                    info="Ignores previously AI generated `modified_lyrics.json` and re-aligns the lyrics with AI."
                )
        gr.HTML("<hr>")

        ##############################################################################
        #                    SECTION 3: SUBTITLES & VIDEO GENERATION
        ##############################################################################
        gr.Markdown("## 3) Subtitles & Video Generation")
        gr.Markdown("### _Generate a karaoke vide using your desired custimization styles and settings._")
        with gr.Row():
            # --- Subtitles basic options ---
            font_input = gr.Dropdown(
                choices=list(available_fonts.keys()),
                value="",
                label="Font"
            )
            primary_color_input = gr.Dropdown(
                choices=available_colors,
                value="White",
                label="Font Color"
            )
            secondary_color_input = gr.Dropdown(
                choices=available_colors,
                value="Yellow",
                label="Font Highlight Color"
            )
            effect_dropdown = gr.Dropdown(
                label="Background Video Effects",
                choices=available_effects,
                value="None",
            )


        with gr.Row():
            subtitle_preview_output = gr.HTML(label="Subtitle Preview",)

        with gr.Accordion("Subtitle Customization Options", open=False):
            with gr.Row():
                fontsize_input = gr.Slider(
                    minimum=12,
                    maximum=84,
                    step=1,
                    value=42,
                    label="Font Size",
                )
                loader_threshold_input = gr.Slider(
                    minimum=5.0,
                    maximum=15.0,
                    step=0.5,
                    value=5.0,
                    label="Loader Threshold (seconds)"
                )

            with gr.Row():
                with gr.Column():
                    outline_color_input = gr.Dropdown(
                        choices=available_colors,
                        value="Black",
                        label="Outline Color"
                    )
                    outline_size_input = gr.Slider(
                        minimum=0,
                        maximum=7,
                        step=1,
                        value=1,
                        label="Outline Size",
                    )

                with gr.Column():
                    shadow_color_input = gr.Dropdown(
                        choices=available_colors,
                        value="Black",
                        label="Shadow Color"
                    )
                    shadow_size_input = gr.Slider(
                        minimum=0,
                        maximum=7,
                        step=1,
                        value=0,
                        label="Shadow Size",
                    )

                with gr.Column():
                    verses_before_input = gr.Slider(
                        minimum=1,
                        maximum=3,
                        step=1,
                        value=2,
                        label="Verses Before",
                    )
                    verses_after_input = gr.Slider(
                        minimum=1,
                        maximum=3,
                        step=1,
                        value=2,
                        label="Verses After",
                    )

        # --- ADVANCED SETTINGS ---
        with gr.Accordion("Advanced Video Settings", open=False):
            gr.Markdown(
                "These options let you tweak video encoding quality, resolution, bitrate, etc.  "
                "Defaults are recommended for most users."
            )
            with gr.Row():
                with gr.Column():
                    resolution_input = gr.Dropdown(
                        choices=["640x480", "1280x720", "1920x1080"],
                        value="1280x720",
                        label="Resolution"
                    )
                    preset_input = gr.Dropdown(
                        choices=["ultrafast", "fast", "medium", "slow"],
                        value="fast",
                        label="FFmpeg Preset"
                    )
                with gr.Column():
                    crf_input = gr.Slider(
                        minimum=0,
                        maximum=51,
                        step=1,
                        value=23,
                        label="CRF (Video Quality)"
                    )
                    fps_input = gr.Slider(
                        minimum=15,
                        maximum=60,
                        step=1,
                        value=24,
                        label="Frames per Second"
                    )
                with gr.Column():
                    bitrate_input = gr.Dropdown(
                        label="Video Bitrate",
                        choices=["1000k", "2000k", "3000k", "4000k", "5000k", "Auto"],
                        value="3000k",
                        interactive=True
                    )
                    audio_bitrate_input = gr.Dropdown(
                        label="Audio Bitrate",
                        choices=["64k", "128k", "192k", "256k", "320k", "Auto"],
                        value="192k",
                        interactive=True
                    )

        with gr.Accordion("Developer Settings", open=False):
            with gr.Row():
                force_subtitles_overwrite = gr.Checkbox(
                    label="Re-Generate Karaoke Subtitles?",
                    value=True,
                    info="If `karaoke_subtitles.ass` already exists, overwrite it with a newly generated file."
                )

        generate_karaoke_button = gr.Button(
            "Generate Karaoke",
            variant="primary",
            interactive=False
        )

        # We can display the final video in a gr.Video component
        karaoke_video_output = gr.Video(label="Karaoke Video", interactive=False)
        gr.HTML("<hr>")

        ##############################################################################
        #             SUBTITLE STYLE PREVIEW (live updates on color/font changes)
        ##############################################################################
        def update_subtitle_preview(*args):
            return generate_font_preview_callback(*args, available_fonts=available_fonts)

        font_preview_inputs = [
            font_input,
            primary_color_input,
            secondary_color_input,
            outline_color_input,
            outline_size_input,
            shadow_color_input,
            shadow_size_input,
        ]

        for component in font_preview_inputs:
            component.change(fn=update_subtitle_preview, inputs=font_preview_inputs, outputs=subtitle_preview_output)

        ##############################################################################
        #             CALLBACK WIRING FOR AUDIO, LYRICS, VIDEO
        ##############################################################################

        # (Primary) Process Audio Button
        # Updates States: working directory, lyrics data, and lyrics to display
        # Displays the updated `state_lyrics_display` in the `raw_lyrics_box`
        process_audio_button.click(
            # `.click()` event: Update the status of our states
            fn=process_audio_callback,
            inputs=[
                audio_input,
                force_meta_fetch,
                force_audio_processing,
                force_transcription,
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

                # Hidden state: cache_dir
                gr.State(cache_dir),
            ],
            outputs=[
                state_working_dir,
                state_lyrics_json,
                state_lyrics_display,
                state_artist_name,
                state_song_name,
            ]
        ).then(
            # `.then()` event: After states are updated, display them in display box
            fn=lambda disp, artist, song: (disp, artist, song),
            inputs=[
                state_lyrics_display,
                state_artist_name,
                state_song_name
            ],
            outputs=[
                raw_lyrics_box,
                artist_name_input,
                song_name_input
            ]
        ).then(
            # After finishing `process_audio_callback`, check if we can enable `Modify with AI` and `Generate Karaoke` buttons
            fn=check_modify_ai_availability,
            inputs=[state_working_dir],
            outputs=modify_button
        ).then(
            fn=check_generate_karaoke_availability,
            inputs=[state_working_dir],
            outputs=generate_karaoke_button
        )

        # (Secondary) 💾 Save Artist and Song Name Button
        save_metadata_button.click(
            fn=save_metadata_callback,
            inputs=[
                state_working_dir,
                artist_name_input,
                song_name_input
            ],
            outputs=[]
        )

        # (Secondary) 🌐 Fetch Reference Lyrics Button
        # Updates States: fetched lyrics, fetched lyrics to display
        # Displays the updated `state_fetched_lyrics_display` in the `fetched_lyrics_box`
        fetch_button.click(
            fn=fetch_reference_lyrics_callback,
            inputs=[
                force_refetch_lyrics,
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
        ).then(
            # After fetching the lyrics, check if we can enable `Modify with AI` button
            fn=check_modify_ai_availability,
            inputs=[state_working_dir],
            outputs=modify_button
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
        ).then(
            # After updating the fetched lyrics, check if we can enable `Modify with AI` button
            fn=check_modify_ai_availability,
            inputs=[state_working_dir],
            outputs=modify_button
        )

        # (Secondary) 🪄 Modify with AI Button
        # Updates States: lyrics, lyrics to display
        # Displays the updated `state_lyrics_display` in the `lyrics_box`
        modify_button.click(
            fn=modify_lyrics_callback,
            inputs=[
                force_ai_modification,
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
        ).then(
            # After lyric modification, check if we can enable `Generate Karaoke` button
            fn=check_generate_karaoke_availability,
            inputs=[state_working_dir],
            outputs=generate_karaoke_button
        )

        # (Primary) Generate Karaoke Button
        # Generates the subtitles and karaoke video
        # Displays the generated video in the `karaoke_video_output`
        generate_karaoke_button.click(
            fn=generate_subtitles_and_video_callback,
            inputs=[
                state_working_dir,

                # Subtitles parameters
                font_input,
                fontsize_input,
                primary_color_input,
                secondary_color_input,
                outline_color_input,
                outline_size_input,
                shadow_color_input,
                shadow_size_input,
                verses_before_input,
                verses_after_input,
                loader_threshold_input,

                # Video parameters
                effect_dropdown,
                resolution_input,
                preset_input,
                crf_input,
                fps_input,
                bitrate_input,
                audio_bitrate_input,

                # Additional or override flags
                force_subtitles_overwrite,

                # Hidden state: output_dir, effects_dir
                gr.State(output_dir),
                gr.State(effects_dir)
            ],
            outputs=[karaoke_video_output]  # or karaoke_status_output, or both
        )

        return app
