"""
utils.py

Utility module for common functions across the project.

Functions:
- log_event(message, level=logging.INFO, logger=None): Logs messages to the controller.log file or the provided logger.
"""

import logging
from logger import setup_logger
import config

# Set up a logger specifically for the controller, using the project_id
controller_logger = setup_logger("controller", config.LOGGING['log_level'], project_id=config.project_id)

def log_event(message, level=logging.INFO, logger=None):
    """
    Logs a message to the controller.log file or a provided logger.

    Args:
        message (str): The message to log.
        level (int): The logging level (e.g., logging.INFO, logging.ERROR).
                     Defaults to logging.INFO.
        logger (logging.Logger, optional): The logger to use. Defaults to controller_logger.
    """
    # Use the provided logger or fall back to the controller logger
    target_logger = logger or controller_logger
    target_logger.log(level, message)
