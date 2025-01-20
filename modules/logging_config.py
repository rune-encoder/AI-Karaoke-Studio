# Standard Library Imports
from logging.handlers import RotatingFileHandler
import logging

# Third-Party Imports
import colorlog


def configure_logging(verbose=False, log_file='project.log'):
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

    # Console formatter with color
    color_formatter = colorlog.ColoredFormatter(
        '%(log_color)s' + log_format,
        datefmt=date_format,
        log_colors={
            'DEBUG': 'white',
            'INFO': 'blue',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'bold_red',
        },
    )

    # File handler with log rotation
    file_handler = RotatingFileHandler(log_file, maxBytes=10**6, backupCount=3)
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
