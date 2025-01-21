# Standard Library Imports
from pathlib import Path
from typing import Union
import logging

# Local Application Imports
from .stem_processing import (process_audio_merging, process_audio_stem_separation)
from .lyrics_processing import (process_audio_extract_lyric_timing)
from .audio_pre_processing import pre_process_audio_file
from .logging_config import configure_logging

# Initialize Logger
logger = logging.getLogger(__name__)

# Pipeline Controller
def run_pipeline(
    input_file: Union[str, Path],
    output_dir: Union[str, Path],
    override_all: bool = False,
    verbose: bool = False,
):
    configure_logging(verbose)

    # ════════════════════════════════════════════════════════════
    # Audio Pre-Processing and Metadata Extraction
    # ════════════════════════════════════════════════════════════
    working_dir = pre_process_audio_file(
        input_file,
        output_dir,
        override=override_all
    )

    # ════════════════════════════════════════════════════════════
    # Stem Separation
    # ════════════════════════════════════════════════════════════
    process_audio_stem_separation(
        input_file, working_dir, override=override_all)

    # ════════════════════════════════════════════════════════════
    # Stem Merging
    # ════════════════════════════════════════════════════════════
    process_audio_merging(working_dir, override=override_all)

    # ════════════════════════════════════════════════════════════
    # Lyric Extraction
    # ════════════════════════════════════════════════════════════
    process_audio_extract_lyric_timing(working_dir, override=override_all)
