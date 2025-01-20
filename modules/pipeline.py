# ════════════════════════════════════════════════════════════
# IMPORTS
# ════════════════════════════════════════════════════════════
# Standard Library Imports
from pathlib import Path
from typing import Union
import logging

# Local Application Imports
from .stem_processing import (process_audio_merging, process_audio_stem_separation)
from .lyrics_processing import (process_audio_extract_lyric_timing)
from .logging_config import configure_logging
from .utilities import (
    normalize_path,
    create_directory,
    validate_audio_file,
    get_file_hash,
)


# Initialize Logger
logger = logging.getLogger(__name__)

# Pipeline Controller
def run_pipeline(
    input_file: Union[str, Path],
    output_dir: Union[str, Path],
    override_all: bool = False,
    verbose: bool = False,
):
    # ════════════════════════════════════════════════════════════
    # Step 1: Validation and Setup
    # ════════════════════════════════════════════════════════════
    configure_logging(verbose)
    
    # Confirm the file is a valid audio file
    if not validate_audio_file(input_file):
        logger.error(f"Invalid audio file: {input_file}")
        return

    file_hash = get_file_hash(input_file)
    working_dir = create_directory(Path(output_dir) / file_hash)
    logger.info(f"Directory: {working_dir}")

    # ════════════════════════════════════════════════════════════
    # Step 2: Stem Separation
    # ════════════════════════════════════════════════════════════
    process_audio_stem_separation(
        input_file, working_dir, override=override_all)

    # ════════════════════════════════════════════════════════════
    # Step 3: Stem Merging
    # ════════════════════════════════════════════════════════════
    process_audio_merging(working_dir, override=override_all)

    # ════════════════════════════════════════════════════════════
    # Step 4: Lyric Extraction
    # ════════════════════════════════════════════════════════════
    process_audio_extract_lyric_timing(working_dir, override=override_all)
