import logging

# Global Project Identifier
project_id = "main"  # Default value for the primary run

# Stop Flags for each project ID
stop_flags = {
    "main": False,  # Default for the main run
    "add1": False,  # Example for an additional run
    # Add more as needed
}

# Logging Configuration
LOGGING = {
    'log_level': logging.DEBUG,
    'log_directory': '/app/wikipedia_scraper/logs/',
    'console_logging': False,  # Default value for console logging
}

# Database Configuration
DB_CONFIG = {
    'user': 'movies_user',
    'password': 'passmvword',
    'host': 'hubuntu.duraturk.org',
    'database': 'movies_gem'
}

# Scraper Configuration
SCRAPER_SETTINGS = {
    'timeout': 10,
    'min_delay': 2,
    'max_delay': 6,
    'user_agents': [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1",
        "Mozilla/5.0 (iPad; CPU OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1"
    ]
}

# Scraper Configuration
BATCH_SIZE = 150
RUN_CONTINUOUSLY = 0  # 0 for infinite, 1 for 1 iteration, N for N iterations
EXTRA_BATCH_DELAY = 3