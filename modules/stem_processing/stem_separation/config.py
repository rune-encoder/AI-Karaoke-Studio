from dataclasses import dataclass

# Default Model and Thresholds
DEFAULT_MODEL = "htdemucs_ft"
DEFAULT_MP3_RATE = 320


@dataclass
class AudioSeparationConfig:
    model: str = DEFAULT_MODEL
    two_stems: str = None
    mp3: bool = True
    mp3_rate: int = DEFAULT_MP3_RATE
    float32: bool = False
    int24: bool = False
