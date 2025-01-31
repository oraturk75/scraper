"""
run_scraper.py

Launcher Script for IMDb Web Scraper

This script serves as the entry point for the IMDb web scraping application.
It initializes the logging system and starts the main controller.

Usage:
    python run_scraper.py
"""

import config
from logger import setup_logger, log_marker
import controller
import time

# Define the project ID for this run
project_id = "main"

logger = setup_logger("run_scraper", config.LOGGING['log_level'], project_id=config.project_id)

if __name__ == "__main__":
    log_marker(logger, f"SCRIPT START [Time: {time.strftime('%Y-%m-%d %H:%M:%S')}]")
    controller.main("main")  # Project ID for the default instance
    log_marker(logger, f"SCRIPT END [Time: {time.strftime('%Y-%m-%d %H:%M:%S')}]")
