"""
imdb_scraper.py

IMDB Scraper Module

This module handles the scraping of language information from IMDb for a given title.

Functions:
- scrape_language(tconst, user_agent): Scrapes the IMDb page for a title and extracts the language.
- delay_between_requests(min_seconds, max_seconds): Introduces a random delay between requests.
- log_script_markers(action): Logs script start or end markers for IMDb Scraper.
"""

import requests
from bs4 import BeautifulSoup
import time
import random
from logger import setup_logger, log_marker
import config

logger = setup_logger(__name__, log_level=config.LOGGING['log_level'], project_id=config.project_id)

def log_script_markers(action):
    """
    Logs script start or end markers for IMDb Scraper.

    Args:
        action (str): Either 'start' or 'end'.
    """
    if action == "start":
        log_marker(logger, f"SCRIPT START [Time: {time.strftime('%Y-%m-%d %H:%M:%S')}]")
    elif action == "end":
        log_marker(logger, f"SCRIPT END [Time: {time.strftime('%Y-%m-%d %H:%M:%S')}]")

def scrape_language(tconst, user_agent):
    """
    Scrapes the IMDb page for a given title (tconst) and extracts the language.

    Args:
        tconst (str): The IMDb title ID (e.g., 'tt0000001').
        user_agent (str): The user agent string to use for the request.

    Returns:
        str: 'E' if English, 'F' if foreign, 'U' if unknown.
    """
    url = f"https://www.imdb.com/title/{tconst}/"
    headers = {'User-Agent': user_agent}
    logger.info(f"Scraping IMDb page: {url} with User-Agent: {user_agent}")
    try:
        response = requests.get(url, headers=headers, timeout=config.SCRAPER_SETTINGS['timeout'])
        logger.info(f"Response status code: {response.status_code}")
        if response.status_code in [403, 429, 503]:
            logger.error(f"Blocking error encountered: {response.status_code}. Stopping script.")
            raise RuntimeError("Blocking error detected.")
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            details = soup.find('section', {'data-testid': 'Details'})
            if not details:
                logger.debug(f"No 'Details' section found on page for {tconst}.")
            if details:
                logger.info(f"Details section found for {tconst}.")
                list_items = details.find_all('li')
                for item in list_items:
                    if any(label in item.text for label in ['Language', 'Languages']):
                        languages = item.find('ul').get_text(strip=True)
                        logger.info(f"Languages found for {tconst}: {languages}")
                        return 'E' if 'English' in languages else 'F'
                logger.warning(f"Language field not found for {tconst}.")
            else:
                logger.warning(f"Details section not found for {tconst}.")
            return 'U'  # Unknown language
    except requests.exceptions.RequestException as e:
        logger.error(f"Request error for {tconst}: {e}")
        return 'U'
    except Exception as e:
        logger.error(f"Error scraping IMDb for {tconst}: {e}")
        return 'U'

def delay_between_requests():
    """
    Introduces a random delay between requests to avoid overloading the server.
    """
    min_seconds = config.SCRAPER_SETTINGS['min_delay']
    max_seconds = config.SCRAPER_SETTINGS['max_delay']
    delay = random.uniform(min_seconds, max_seconds)
    logger.info(f"Delaying next request by {delay:.2f} seconds.")
    time.sleep(delay)