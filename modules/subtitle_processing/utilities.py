import subprocess

def extract_audio_duration(audio_path):
    """
    Get the duration of an audio file using ffprobe.
    """
    try:
        # Run the ffprobe command to extract the duration of the audio file
        result = subprocess.run(
            [
                "ffprobe",                              # Command to run ffprobe
                "-i", audio_path,                       # Input file path
                "-show_entries", "format=duration",     # Request only the duration metadata
                "-v", "quiet",                          # Suppress unnecessary output
                "-of", "csv=p=0"                        # Format the output as plain CSV with no headers
            ],
            stdout=subprocess.PIPE,                     # Capture the standard output
            stderr=subprocess.PIPE,                     # Capture the standard error
            check=True                                  # Raise CalledProcessError if the command fails
        )

        # Decode the stdout result to a string, strip whitespace, and convert to float
        duration = float(result.stdout.decode("utf-8").strip())
        return duration  # Return the duration in seconds

    except subprocess.CalledProcessError as e:
        # Handle errors from ffprobe (e.g., if the command fails or the file is invalid)
        raise RuntimeError(f"ffprobe failed: {e.stderr.decode('utf-8')}") from e

    except ValueError as e:
        # Handle cases where the output cannot be converted to a float
        raise ValueError("Invalid duration format received from ffprobe.") from e

    except Exception as e:
        # Handle any other unexpected errors
        raise RuntimeError(f"Unexpected error: {e}") from e


def get_ass_rounded_rectangle(
    width: int,
    height: int,
    radius: int
) -> str:
    """
    Return rectangle with rounded corners in ASS format
    """
    if width == 0 or height == 0 or radius * 2 > width or radius * 2 > height:
        return ''

    bezier = radius * 0.414
    rect = f"\
{{\\p1}}m {radius} 0 \
l {width-radius} 0 \
b {width-bezier} 0 {width} {bezier} {width} {radius} \
l {width} {height-radius} \
l {width} {height-radius} \
b {width} {height-bezier} {width-bezier} {height} {width-radius} {height} \
l {radius} {height} \
b {bezier} {height} 0 {height-bezier} 0 {height-radius} \
l 0 {radius} \
l 0 {radius} \
b 0 {bezier} {bezier} 0 {radius} 0{{\\p0}}"

    return rect
