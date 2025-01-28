# Note: Code has been modified and repurposed to work locally and with local hardware and computer.
# Original code obtained from https://colab.research.google.com/drive/1dC9nVxk3V_VPjUADsnFu8EiT-xnU1tGH?usp=sharing#scrollTo=79JbZGcAqX3p
# Reference Model Source from GitHub https://github.com/facebookresearch/demucs

"""
This script is designed to separate audio files into different stems using the Demucs model.
It has been modified and repurposed to work locally with local hardware and computer.

Original code obtained from:
https://colab.research.google.com/drive/1dC9nVxk3V_VPjUADsnFu8EiT-xnU1tGH?usp=sharing#scrollTo=79JbZGcAqX3p

Reference Model Source from GitHub:
https://github.com/facebookresearch/demucs
"""
# Standard Library Imports
from pathlib import Path
from typing import Union
import logging

# Third-Party Imports
import torch

# Local Application Imports
from .config import AudioSeparationConfig
from .utilities import (
    _execute_command,
    _organize_outputs,
)

# Initialize Logger
logger = logging.getLogger(__name__)


def _excecute_stem_separation(
    input_file: Union[str, Path],
    output_path: Union[str, Path],
    config: AudioSeparationConfig = AudioSeparationConfig(),
):
    try:
        input_path = Path(input_file)
        output_path = Path(output_path)

        # Set the device for processing the audio
        device = torch.device(
            f"cuda:{torch.cuda.current_device()}" if torch.cuda.is_available() else "cpu")

        # Prepare the command to execute the Demucs model
        cmd = [
            "python", "-m", "demucs.separate",
            "-o", str(output_path),
            "-n", config.model,
            "--device", f"{device}"
        ]

        if config.mp3:
            cmd += ["--mp3", f"--mp3-bitrate={config.mp3_rate}"]

        if config.float32:
            cmd += ["--float32"]

        if config.int24:
            cmd += ["--int24"]

        if config.two_stems is not None:
            cmd += [f"--two-stems={config.two_stems}"]

        cmd.append(str(input_path))
        logger.debug(f"Executing command: {' '.join(cmd)}")

        # Execute the command to separate the audio stems using subprocess
        if not _execute_command(cmd):
            # Early exit if the command fails
            return

        # Organize the output files removing them from subdirectories
        _organize_outputs(output_path)

    except Exception as e:
        logger.error(f"Error in stem separation: {e}")
        raise RuntimeError(f"Error in stem separation: {e}")
