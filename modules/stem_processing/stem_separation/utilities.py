from pathlib import Path
import subprocess as sp
import logging
import shutil

logging.basicConfig(level=logging.INFO)

def _organize_outputs(output_path):
    """
    Organize output files by moving them from subdirectories to the main output directory.

    Args:
        output_path (str): Path to the main output directory.
    """
    # Convert the output path to a Path object
    output_dir = Path(output_path)

    # Iterate through each item in the output directory
    for model_dir in output_dir.iterdir():

        # Check if the item is a directory
        if model_dir.is_dir():

            # Recursively find all files in the subdirectory
            for file in model_dir.glob("**/*"):

                # Check if the item is a file
                if file.is_file():

                    # Define the new location for the file in the main output directory
                    new_location = output_dir / file.name

                    # Move the file to the new location
                    shutil.move(str(file), new_location)

            # Remove the now-empty subdirectory
            shutil.rmtree(model_dir)


def _execute_command(cmd):
    """
    Execute a shell command and handle stdout and stderr.

    Args:
        cmd (list): Command to execute.

    Returns:
        bool: True if the command executed successfully, False otherwise.
    """
    try:
        # Execute the separation command using subprocess
        process = sp.Popen(cmd, stdout=sp.PIPE, stderr=sp.PIPE)

        # Handle the I/O streams of the process, capturing stdout and stderr
        stdout, stderr = process.communicate()

        # if stdout:
        #     sys.stdout.write(stdout.decode())

        # if stderr:
        #     sys.stderr.write(stderr.decode())

        if stdout:
            logging.info(stdout.decode())

        if stderr:
            logging.warning(stderr.decode())

        # Wait for the process to finish
        process.wait()

        if process.returncode != 0:
            raise RuntimeError(
                f"Command failed with return code {process.returncode}.")
        return True

    except Exception as e:
        logging.error(f"Command execution failed: {e}")
        raise
