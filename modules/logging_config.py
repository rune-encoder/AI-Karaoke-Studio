# Standard Library Imports
from logging.handlers import RotatingFileHandler
import logging
import os
from datetime import datetime, timedelta

# Third-Party Imports
import colorlog


def _create_logs_folder(folder_path='logs'):
    """
    Ensures the logs folder exists.
    """
    os.makedirs(folder_path, exist_ok=True)
    return folder_path


def _get_log_filename(folder_path):
    """
    Generates a log file name based on the current date and time.
    """
    # Get the current date and time
    timestamp = datetime.now().strftime('%m-%d-%Y_%H-%M-%S')

    # Generate the log file path
    log_file_path = os.path.join(folder_path, f'{timestamp}.log')

    return log_file_path


def _cleanup_old_logs_by_days(folder_path, retention_days=7):
    """
    Deletes log files older than the retention period.

    Args:
        folder_path (str): Path to the logs folder.
        retention_days (int): Number of days to retain log files.
    """
    # Get the current date and time
    now = datetime.now()

    # Iterate over the files in the logs folder
    for filename in os.listdir(folder_path):

        # Get the full file path
        file_path = os.path.join(folder_path, filename)

        # Check if the file is a log file. Only process log files
        if os.path.isfile(file_path):

            # If the file is a log file, get the creation time
            file_creation_time = datetime.fromtimestamp(os.path.getctime(file_path))
            
            # Check if the file is older than the retention period
            if now - file_creation_time > timedelta(days=retention_days):

                # If the file is older than the retention period, delete it
                os.remove(file_path)


def _cleanup_logs_by_number(folder_path, max_logs=10):
    """
    Ensures that only the newest `max_logs` log files remain in the folder.
    Removes the oldest files if the count exceeds `max_logs`.
    """
    # Get a list of *.log files in the folder
    log_files = [f for f in os.listdir(folder_path) if f.endswith('.log')]
    
    # If total logs are within the limit, nothing to do
    if len(log_files) <= max_logs:
        return

    # Sort files by creation time (oldest first)
    log_files.sort(key=lambda f: os.path.getctime(os.path.join(folder_path, f)))

    # Number of files to remove
    files_to_remove = len(log_files) - max_logs

    # Remove the oldest files
    for i in range(files_to_remove):
        os.remove(os.path.join(folder_path, log_files[i]))


def configure_logging(verbose=False, logs_folder='logs', max_logs=10):
    """
    Configures the root logger with verbosity and formatting.

    Args:
        verbose (bool): If True, set log level to DEBUG. Otherwise, INFO.
        log_file (str): File to log messages.
    """
    log_level = logging.DEBUG if verbose else logging.INFO

    # Formatter strings
    date_format = '%Y-%m-%d %H:%M'
    if verbose:
        log_format = '%(asctime)s - [%(name)s] - %(levelname)s - %(message)s'
    else:
        log_format = '%(asctime)s - %(levelname)s - %(message)s'

    # File formatter
    file_formatter = logging.Formatter(log_format, datefmt=date_format)

    # Ensure logs folder exists
    logs_path = _create_logs_folder(logs_folder)

    # Cleanup old logs
    _cleanup_logs_by_number(logs_path, max_logs)

    # Get log file path
    log_file = _get_log_filename(logs_path)

    # Console formatter with color
    color_formatter = colorlog.ColoredFormatter(
        '%(log_color)s' + log_format,
        datefmt=date_format,
        log_colors={
            'DEBUG': 'white',
            'INFO': 'green',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'bold_red',
        },
    )

    # File handler with log rotation
    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(file_formatter)
    file_handler.setLevel(log_level)

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(color_formatter)
    console_handler.setLevel(log_level)

    # Root logger configuration
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)

    # Avoid duplicate logs
    root_logger.propagate = False

if __name__ == '__main__':
    configure_logging(verbose=True)
    logger = logging.getLogger(__name__)
    logger.debug('This is a debug message')
    logger.info('This is an info message')
    logger.warning('This is a warning message')
    logger.error('This is an error message')
    logger.critical('This is a critical message')
