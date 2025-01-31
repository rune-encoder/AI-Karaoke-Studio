# Standard Library Imports
from typing import Union, Optional
from pathlib import Path
import subprocess
import logging

# Third-Party Imports
import torch

from .utilities import extract_audio_duration, validate_file
# Initialize Logger
logger = logging.getLogger(__name__)


def generate_karaoke_video(
    audio_path: Union[str, Path],
    ass_path: Union[str, Path],
    output_path: Union[str, Path],
    video_effect: Union[str, Path],
    resolution: str = "1280x720",
    preset: str = "fast",
    crf: Optional[int] = 23,   # CRF may be irrelevant for NVENC
    fps: int = 24,
    bitrate: str = "3000k",
    audio_bitrate: str = "192k",
):
    """
    Generate a karaoke video by:
      1) Looping an "effect video" infinitely for the entire duration,
      2) Scaling/padding the effect video to the desired resolution,
      3) Overlaying .ass subtitles (karaoke_subtitles.ass),
      4) Mapping the user-supplied audio track,
      5) Writing the final video to `output_path`.

    Args:
        audio_path (str|Path): Path to the karaoke audio (.mp3 or similar).
        ass_path (str|Path): Path to the .ass subtitles.
        output_path (str|Path): Destination for the final MP4.
        resolution (str): E.g. "1280x720".
        preset (str): FFmpeg encoding preset (ultrafast, fast, medium, slow, etc.).
        crf (int|None): Quality setting for CPU-based x264 (GPU often ignores this).
        fps (int): Frames per second for the output video.
        bitrate (str): Target video bitrate (e.g. "3000k").
        audio_bitrate (str): Audio bitrate (e.g. "192k").

    Returns:
        str|None: Returns the final output path (str) on success, or None on failure.
    """
    # video_effect = Path(r"C:\Users\chris\ai_karaoke_app\effects\snow.mp4").as_posix()

    if not validate_file(audio_path):
        logger.error(f"Invalid audio file: {audio_path}")
        return None
    if not validate_file(ass_path):
        logger.error(f"Invalid .ass subtitles: {ass_path}")
        return None

    # Check for GPU vs CPU
    if torch.cuda.is_available():
        device_name = torch.cuda.get_device_name(0)
        logger.info(f"GPU found: {device_name} (NVENC).")
        video_codec = "h264_nvenc"
        use_crf = False
    else:
        logger.warning("[WARN] No GPU found, using libx264 (CPU).")
        video_codec = "libx264"
        use_crf = True

    # Get audio duration
    audio_dur = extract_audio_duration(audio_path)
    if audio_dur is None:
        logger.error("Cannot detect audio duration, aborting.")
        return None

    ############################################################################
    # Build the FMPEG command
    ############################################################################
    cmd = ["ffmpeg", "-y"]

    if video_effect is not None:
        if not validate_file(video_effect):
            logger.error(f"Video_effect is invalid: {video_effect}")
            return None
        
        # Input #0 => effect video, loop infinitely (-1)
        cmd.extend(["-stream_loop", "-1", "-i", str(video_effect)])
    else:
        # Input #0 => black background
        cmd.extend(["-f", "lavfi", "-i", f"color=c=black:s={resolution}:d={audio_dur}"])

    # Input #1 => karaoke audio
    cmd.extend(["-i", str(audio_path)])

    # We'll parse resolution into width/height for scale/pad
    width, height = resolution.split("x")

    filter_chain = (
        f"[0:v]"
        # scale to the desired resolution
        f"scale={width}:{height}:force_original_aspect_ratio=decrease,"
        # pad so that if aspect ratio differs, we fill the entire {width}x{height}
        f"pad=w={width}:h={height}:x='(ow - iw)/2':y='(oh - ih)/2'[bg];"
        # apply .ass subtitles => [vout]
        f"[bg]subtitles={ass_path}[vout]"
    )

    # We'll map final video from [vout], audio from input #1
    cmd.extend([
        "-filter_complex", filter_chain,
        "-map", "[vout]",
        "-map", "1:a"
    ])

    # Output encoding settings
    cmd.extend([
        "-pix_fmt", "yuv420p",
        "-c:v", video_codec,
        "-preset", preset
    ])

    if use_crf and crf is not None:
        cmd.extend(["-crf", str(crf)])

    cmd.extend([
        "-r", str(fps),
        "-b:v", str(bitrate),
        "-c:a", "aac",
        "-b:a", str(audio_bitrate),
        "-shortest",  # stop at the shortest stream (audio vs. effect video)
        str(output_path)
    ])

    # Debug: print the ffmpeg command
    logger.debug("FFmpeg command: %s", " ".join(cmd))

    # Execute FFmpeg
    try:
        subprocess.run(cmd, check=True)
        logger.info(f"Karaoke video created at: {output_path}")
        return str(output_path)
    except subprocess.CalledProcessError as e:
        logger.error(f"FFmpeg error: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return None
