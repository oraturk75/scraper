"""
Logger Module

This module provides a centralized and configurable logging system for Python scripts. It allows scripts to log messages to individual log files and optionally output logs to the console. Each script can have a unique logger instance to ensure isolated and clear logging.

Features:
- Configurable log level (default: DEBUG).
- Supports both file and console logging.
- Unique logger instances for each script using the script's __name__.
- Example usage provided for easy integration.

Configuration:
- LOG_LEVEL: Default logging level. Can be set globally or overridden per script.
- LOG_DIRECTORY: Directory where log files are stored (default: /app/logs/).

Usage:
1. Import the logger module in your script:
    from logger import setup_logger, log_marker

2. Setup the logger:
    logger = setup_logger(__name__, log_level=logging.INFO)

3. Use the logger instance to log messages:
    logger.info("This is an info message.")
    logger.debug("This is a debug message.")
    logger.error("This is an error message.")

4. Add visual markers:
    log_marker(logger, "SCRIPT START")
    log_marker(logger, "SCRIPT END")

Example:
(See below for example usage)
"""

import logging
import os
from config import LOGGING

class ProjectIDFormatter(logging.Formatter):
    """
    Custom formatter that dynamically retrieves the project_id from the logger instance.
    """
    def format(self, record):
        logger = logging.getLogger(record.name)
        if hasattr(logger, 'project_id'):
            record.project_id = logger.project_id  # Get from the logger
        else:
            record.project_id = "unknown"  # Avoid hardcoding 'default' here
        return super().format(record)

def setup_logger(name, log_level=None, project_id=None, console_logging=False):
    """
    Setup a logger with the given name and configuration.

    Args:
        name (str): Name of the logger, typically __name__.
        log_level (int): Logging level (e.g., logging.DEBUG, logging.INFO).
        project_id (str): Identifier for the project/run. Defaults to config.project_id.
        console_logging (bool): If True, log messages are also printed to the console.

    Returns:
        logging.Logger: Configured logger instance with project_id attribute.
    """
    # Use default log level from config if not provided
    if log_level is None:
        log_level = LOGGING['log_level']

    # Use default project_id from config if not provided
    if project_id is None:
        project_id = LOGGING.get('project_id', 'default')

    # Ensure the log directory exists and include project_id for isolation
    log_directory = os.path.join(LOGGING['log_directory'], project_id)
    os.makedirs(log_directory, exist_ok=True)

    # Define log file path within the project-specific directory
    log_file = os.path.join(log_directory, f"{name}.log")

    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(log_level)

    # Add project_id as an attribute to the logger
    logger.project_id = project_id

    # Check if handlers are already attached
    if not logger.hasHandlers():
        # File handler
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(log_level)
        file_formatter = ProjectIDFormatter(
            '%(asctime)s - %(project_id)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

        # Optional console handler
        if console_logging:
            console_handler = logging.StreamHandler()
            console_handler.setLevel(log_level)
            console_formatter = ProjectIDFormatter(
                '%(asctime)s - %(project_id)s - %(name)s - %(levelname)s - %(message)s'
            )
            console_handler.setFormatter(console_formatter)
            logger.addHandler(console_handler)

    return logger

def log_marker(logger, marker):
    """
    Logs a visual marker to indicate significant events (e.g., script start/end).

    Args:
        logger (logging.Logger): The logger instance.
        marker (str): The marker message to log.

    Returns:
        None
    """
    separator = "=" * 50
    logger.info(separator)
    logger.info(f"{getattr(logger, 'project_id', 'unknown')} - {marker}")
    logger.info(separator)
