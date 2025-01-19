# ════════════════════════════════════════════════════════════
# IMPORTS
# ════════════════════════════════════════════════════════════
import logging
from pathlib import Path

from typing import Union

from .stem_processing import (process_audio_merging, process_audio_stem_separation)
from .lyrics_processing import (process_audio_extract_lyric_timing)

from .utilities import (
    normalize_path,
    create_directory,
    validate_audio_file,
    get_file_hash,
)

logging.basicConfig(level=logging.INFO)

# Pipeline Controller
def run_pipeline(
    input_file: Union[str, Path],
    output_dir: Union[str, Path],
    override_all: bool = False
):
    # ════════════════════════════════════════════════════════════
    # Step 1: Validation and Setup
    # ════════════════════════════════════════════════════════════

    # Confirm the file is a valid audio file
    if not validate_audio_file(input_file):
        logging.error(f"Invalid audio file: {input_file}")
        return

    file_hash = get_file_hash(input_file)
    working_dir = create_directory(Path(output_dir) / file_hash)
    logging.info(f"Working Directory: {working_dir}")

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

    logging.info("Pipeline completed successfully.")
