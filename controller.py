"""
controller.py

Controller Module

This module orchestrates the IMDb scraping process, serving as the central workflow manager.
It coordinates interactions between the Database, IMDbScraper, and Logger modules to ensure 
efficient and traceable processing of movie titles.

Responsibilities:
- Fetch titles marked as 'pending' from the database.
- Scrape language data for each title using the IMDbScraper module.
- Update the database with the results, including status changes ('processing', 'complete', 'failed').
- Log detailed progress and key events for debugging and auditing.

Key Functions:
- process_title(title, user_agent): Processes a single title by fetching its language data.
- process_batch(batch_iteration, total_iterations): Handles batch processing, including fetching,
  scraping, and updating multiple titles in a single iteration.
- main(): Entry point for the controller script, manages the execution loop based on configuration.

Example Usage:
    This script is designed to be invoked by `run_scraper.py`. Ensure configuration settings 
    are updated in `config.py` before execution.

"""

import time
import random
from logger import setup_logger, log_marker
import config
from db_connector import Database
from imdb_scraper import scrape_language, delay_between_requests, log_script_markers
import utils
import importlib

logger = setup_logger(__name__, log_level=config.LOGGING['log_level'], project_id=config.project_id)

def process_title(title, user_agent):
    ###
    # Processes a single movie title by determining its language and updating its status.
    #
    # Args:
    #     title (dict): A dictionary containing title data, including:
    #         - tconst (str): The unique IMDb ID for the title.
    #         - primaryTitle (str): The primary title of the movie.
    #     user_agent (str): The user agent string to use for the HTTP request.
    #
    # Returns:
    #     tuple: 
    #         - tconst (str): The IMDb ID of the processed title.
    #         - is_foreign (str): 'E' (English), 'F' (Foreign), or 'U' (Unknown) based on the detected language.
    #         - status (str): 'complete' if the language was successfully determined, otherwise 'failed'.
    #
    # Notes:
    #     - Relies on the `scrape_language` function from the IMDbScraper module to classify the title's language.
    #     - Logs the start and end of the processing for traceability.
    #     - Handles unexpected issues by marking the status as 'failed'.
    ###
    logger.info(f"Processing title {title['tconst']} - {title['primaryTitle']}.")
    is_foreign = scrape_language(title['tconst'], user_agent)
    status = 'complete' if is_foreign != 'U' else 'failed'
    return (title['tconst'], is_foreign, status)

def process_batch(batch_iteration, total_iterations):
    ###
    # Processes a batch of titles by fetching, scraping, and updating their statuses.
    #
    # Args:
    #     batch_iteration (int): The current iteration number of the batch process.
    #     total_iterations (int): Total number of iterations to run ('continuous' if infinite).
    #
    # Steps:
    #     1. Fetches titles with 'pending' status from the database.
    #     2. Scrapes language data for each title.
    #     3. Updates the database with the results, including status changes.
    #     4. Logs start and end of the batch for traceability.
    #
    # Notes:
    #     - Logs an informational message if no pending titles are available.
    #     - Delays between requests to avoid overwhelming external servers.
    ###
    batch_start_time = time.time()

    log_marker(logger, f"BATCH START [Iteration: {batch_iteration} of {total_iterations}, Time: {time.strftime('%Y-%m-%d %H:%M:%S')}]")

    # Add IMDb scraper script start marker
    log_script_markers("start")

    with Database(config.DB_CONFIG) as db:
        titles = db.fetch_titles(config.BATCH_SIZE)

        if not titles:
            logger.info("No pending titles found. Skipping batch processing.")
            log_script_markers("end")  # End marker for empty batch
            return

        results = []
        for title in titles:
            user_agent = random.choice(config.SCRAPER_SETTINGS['user_agents'])
            result = process_title(title, user_agent)
            results.append(result)
            delay_between_requests()

        db.update_batch_results(results)

    duration = time.time() - batch_start_time
    minutes, seconds = divmod(int(duration), 60)
    logger.info(f"This {batch_iteration} iteration of the batch took {minutes} mins {seconds} secs to complete.")

    # Add IMDb scraper script end marker
    log_script_markers("end")

    log_marker(logger, f"BATCH END [Iteration: {batch_iteration} of {total_iterations}, Time: {time.strftime('%Y-%m-%d %H:%M:%S')}]")

    logger.info(f"Delaying next batch by {config.EXTRA_BATCH_DELAY} seconds.")
    time.sleep(config.EXTRA_BATCH_DELAY)

def main(project_id):
    ###
    # Entry point for the controller script.
    #
    # Steps:
    #     1. Initializes the batch iteration counter.
    #     2. Enters a loop to process batches based on configuration.
    #     3. Reloads configuration dynamically to reflect changes during runtime.
    #     4. Monitors and respects stop flags for graceful shutdown.
    #     5. Stops execution after completing configured iterations or upon stop request.
    #
    # Notes:
    #     - Designed to work with the `RUN_CONTINUOUSLY` configuration for flexible iteration control.
    #     - Logs the start and end of the script execution for traceability.
    ###
    config.project_id = project_id  # Dynamically set the project_id
    log_marker(logger, f"SCRIPT START [Time: {time.strftime('%Y-%m-%d %H:%M:%S')}]")
    batch_iteration = 0
    total_iterations = "continuous" if config.RUN_CONTINUOUSLY == 0 else config.RUN_CONTINUOUSLY
    try:
        while True:
            batch_iteration += 1
            # Removed redundant log_marker call here
            process_batch(batch_iteration, total_iterations)

            # Reload the config file
            importlib.reload(config)

            # Debugging: Log the current value of the stop flag
            stop_flag_value = config.stop_flags.get(config.project_id, False)
            logger.debug(f"Current stop flag value for project ID '{config.project_id}': {stop_flag_value}")
            
            # Check the graceful stop flag after each batch
            if stop_flag_value:
                logger.info(f"Graceful stop requested for project ID: {config.project_id}. Stopping execution.")
                break
            
            # Stop execution if it's not a continuous run and iteration limit is reached
            if config.RUN_CONTINUOUSLY > 0 and batch_iteration >= config.RUN_CONTINUOUSLY:
                logger.info(f"All {config.RUN_CONTINUOUSLY} iterations completed. Stopping execution.")
                break
    except KeyboardInterrupt:
        logger.info("Script interrupted by user.")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
    finally:
        # Reset stop flag in the config file
        try:
            with open("config.py", "r") as file:
                lines = file.readlines()

            with open("config.py", "w") as file:
                for line in lines:
                    if f'"{config.project_id}": True' in line:
                        line = line.replace("True", "False")
                    file.write(line)

            logger.info(f"Stop flag for project ID '{config.project_id}' has been reset to False in the config file.")
        except Exception as e:
            logger.error(f"Failed to reset stop flag in config file: {e}")

        log_marker(logger, f"SCRIPT END [Time: {time.strftime('%Y-%m-%d %H:%M:%S')}]")
        if logger.hasHandlers():
            logger.handlers[0].flush()

if __name__ == "__main__":
    main()
