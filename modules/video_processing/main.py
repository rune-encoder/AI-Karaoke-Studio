import torch
import subprocess
from pathlib import Path
from PIL import Image
from .utilities import extract_audio_duration, validate_file

def preprocess_image(image_path, resolution):
    output_path = str(Path("./audio_processing/karaoke_files/preprocessed_images/temp_image.png"))
    try:
        img = Image.open(image_path)
        # Ensure RGB format
        img = img.convert("RGB")  
        width, height = map(int, resolution.split("x"))
        # Match video resolution
        img = img.resize((width, height))  
        img.save(output_path, "PNG")
        return output_path
    except Exception as e:
        print(f"Error processing image: {e}")
        return None

def generate_karaoke_video(
    audio_path,
    ass_path,
    output_path,
    resolution="1280x720",
    preset="fast",
    crf=23,
    fps=24,
    bitrate="3000k",
    audio_bitrate="192k",
    background_image=None, 
):
    """
    Generate a karaoke video with a black background, utilizing GPU acceleration if available.

    Parameters:
    - audio_path (str): Path to the input audio file.
    - ass_path (str): Path to the ASS subtitle file.
    - output_path (str): Path to save the generated video.
    - resolution (str): Video resolution (default: "1280x720").
    - preset (str): FFmpeg encoding preset for speed/quality tradeoff (default: "fast").
    - crf (int): Quality setting for video encoding (lower is better, default: 23).
    - fps (int): Frames per second for the video (default: 24).
    - bitrate (str): Video bitrate for quality control (default: "3000k").
    - audio_bitrate (str): Audio bitrate for output quality (default: "192k").
    """

    # Validate input files
    if not validate_file(audio_path) or not validate_file(ass_path):
        return

    # Check for GPU availability
    if torch.cuda.is_available():
        # Use NVIDIA NVENC for GPU acceleration
        device = torch.cuda.get_device_name(0)
        print(f"✅ GPU detected: {device}")
        video_codec = "h264_nvenc"  
    else:
        # Use CPU codec
        print("⚠️ No GPU detected. Falling back to CPU.")
        video_codec = "libx264"  

    # Get audio duration
    audio_duration = extract_audio_duration(audio_path)
    if audio_duration is None:
        print("❌ Unable to retrieve audio duration. Aborting.")
        return

    if background_image:
        background_image = preprocess_image(background_image, resolution)
        if not background_image:
            return "Error processing background image."

# Build FFmpeg command
    command = ["ffmpeg", "-y"]  # Overwrite output

    if background_image:
        # Add background image
        command.extend(["-loop", "1", "-i", background_image])  # Loop the background image
        # Add audio input
        command.extend(["-i", audio_path])
        # Filter complex for scaling and subtitles
        filter_complex = f"[0:v]scale={resolution},subtitles={ass_path}"
        command.extend(["-filter_complex", filter_complex])
        # Map video and audio streams
        command.extend(["-map", "0:v", "-map", "1:a"])
    else:
        # Add a black background
        command.extend(["-f", "lavfi", "-i", f"color=c=black:s={resolution}:d={audio_duration}"])  # Black background
        # Add audio input
        command.extend(["-i", audio_path])
        # Add subtitles directly
        command.extend(["-vf", f"subtitles={ass_path}"])

    # Add common video and audio options
    command.extend([
        "-pix_fmt", "yuv420p",  # Set standard pixel format
        "-c:v", video_codec,  # Video codec
        "-preset", preset,    # Encoding preset
        "-crf", str(crf),     # Quality level
        "-r", str(fps),       # Frame rate
        "-b:v", bitrate,      # Video bitrate
        "-c:a", "aac",        # Audio codec
        "-b:a", audio_bitrate,  # Audio bitrate
        "-shortest",  # Match shortest stream
        output_path  # Output file
    ])

    # Debugging: Print the constructed command
    print("\nRunning FFmpeg command:")
    print(" ".join(command))

    # Execute FFmpeg command
    try:
        subprocess.run(command, check=True)
        print(f"✅ Video successfully created at: {output_path}")
    except subprocess.CalledProcessError as e:
        print(f"❌ FFmpeg error: {e}")
    except Exception as e:
        print(f"❌ An unexpected error occurred: {e}")