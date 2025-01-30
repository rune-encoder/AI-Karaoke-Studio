import torch
import subprocess
from pathlib import Path
from PIL import Image
from typing import Union, Optional
from .utilities import extract_audio_duration, validate_file
import logging

logger = logging.getLogger(__name__)

# ! REFERENCE CRF AND IMPROVE FOR CPU AND GPU USAGE

def preprocess_image(image_path, resolution):
    """
    Load and resize the given background image to match `resolution`.
    Returns a temporary file path to the processed PNG.
    """
    import tempfile
    try:
        with Image.open(image_path) as img:
            img = img.convert("RGB")
            width, height = map(int, resolution.split("x"))
            img = img.resize((width, height))

            with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
                output_path = tmp.name
            img.save(output_path, "PNG")
            return output_path
    except Exception as e:
        logger.error(f"Error processing image: {e}")
        return None

def generate_karaoke_video(
    audio_path: Union[str, Path],
    ass_path: Union[str, Path],
    output_path: Union[str, Path],
    resolution: str = "1280x720",
    preset: str = "fast",
    crf: Optional[int] = 23,   # CRF might be irrelevant for NVENC
    fps: int = 24,
    bitrate: str = "3000k",
    audio_bitrate: str = "192k",
    background_image: Optional[Union[str, Path]] = None
):
    """
    Generate a karaoke video with either:
      - A looped background image
      - Or a black background (default)

    Tries GPU acceleration (NVENC) if available via torch.cuda.
    Otherwise falls back to libx264 CPU encoding.
    """
    # Validate input files
    if not validate_file(audio_path):
        logger.error(f"Invalid audio file: {audio_path}")
        return
    if not validate_file(ass_path):
        logger.error(f"Invalid subtitle file: {ass_path}")
        return

    # Check GPU
    if torch.cuda.is_available():
        device_name = torch.cuda.get_device_name(0)
        logger.info(f"[OK] GPU detected: {device_name}")
        video_codec = "h264_nvenc"
        # If you want CRF-like control, consider removing -crf and using:
        #   command.extend(["-rc:v", "vbr_hq", "-cq:v", str(crf)])  # if crf is integer
    else:
        logger.warning("[BAD] No GPU detected. Falling back to CPU (libx264).")
        video_codec = "libx264"

    # Get audio duration
    audio_duration = extract_audio_duration(audio_path)
    if audio_duration is None:
        logger.error("[BAD] Unable to retrieve audio duration. Aborting.")
        return

    # Preprocess background image if provided
    if background_image:
        background_image = preprocess_image(background_image, resolution)
        if not background_image:
            return "Error processing background image."

    # Build FFmpeg command
    command = ["ffmpeg", "-y"]  # Overwrite output

    if background_image:
        # 1) Loop the background image
        command.extend(["-loop", "1", "-i", background_image])
        # 2) Audio input
        command.extend(["-i", str(audio_path)])
        # 3) Filter: scale + subtitles
        filter_complex = f"[0:v]scale={resolution},subtitles={ass_path}"
        command.extend(["-filter_complex", filter_complex])
        # 4) Map streams
        command.extend(["-map", "0:v", "-map", "1:a"])
    else:
        # Black background for the duration
        command.extend(["-f", "lavfi", "-i", f"color=c=black:s={resolution}:d={audio_duration}"])
        command.extend(["-i", str(audio_path)])
        # Subtitles directly
        command.extend(["-vf", f"subtitles={ass_path}"])

    # Common video/audio settings
    command.extend([
        "-pix_fmt", "yuv420p",
        "-c:v", video_codec,
        "-preset", preset,
    ])

    # CRF might be ignored for NVENC, but let's keep it for CPU
    if not torch.cuda.is_available() and crf is not None:
        command.extend(["-crf", str(crf)])

    command.extend([
        "-r", str(fps),
        "-b:v", str(bitrate),
        "-c:a", "aac",
        "-b:a", str(audio_bitrate),
        "-shortest",      # Stop at the shortest input
        str(output_path)  # Output file
    ])

    # Debug
    logger.debug("FFmpeg command: %s", " ".join(command))

    try:
        subprocess.run(command, check=True)
        logger.info(f"[OK] Video successfully created at: {output_path}")
    except subprocess.CalledProcessError as e:
        logger.error(f"[BAD] FFmpeg error: {e}")
    except Exception as e:
        logger.error(f"[BAD] An unexpected error occurred: {e}")
