"""
run_scraper_add1.py

Launcher Script for IMDb Web Scraper - Instance 1

This script launches an additional instance of the IMDb scraper with 
specific configurations for parallel processing.

Usage:
    python run_scraper_add1.py
"""

import config
from logger import setup_logger, log_marker
import controller
import time

# Define the project ID for this instance
config.project_id = "add1"  # Unique identifier for this instance

# Optionally override other configurations for this instance
config.BATCH_SIZE = 10  # Example: Adjust batch size for this instance

logger = setup_logger("run_scraper_add1", config.LOGGING['log_level'], project_id=config.project_id)

if __name__ == "__main__":
    log_marker(logger, f"SCRIPT START [Time: {time.strftime('%Y-%m-%d %H:%M:%S')}]")
    controller.main("add1")  # Project ID for this additional instance
    log_marker(logger, f"SCRIPT END [Time: {time.strftime('%Y-%m-%d %H:%M:%S')}]")
