"""
db_connector.py

Database Connector Module

This module provides a class for interacting with the MariaDB database.
It encapsulates database connection, disconnection, and query execution logic.

Features:
- Connection and disconnection management using context manager.
- Methods for fetching titles and updating batch results.
- Error handling and logging for database operations.
- Configurable SQL queries.

Usage:
1. Import the Database class:
    from db_connector import Database

2. Use the 'with' statement to manage database connection:
    with Database(config.DB_CONFIG) as db:
        # Perform database operations within this block
        titles = db.fetch_titles(config.BATCH_SIZE)
        db.update_batch_results(results)

    # Connection is automatically closed when exiting the 'with' block

Note:
- Script markers (`SCRIPT START` and `SCRIPT END`) are logged within the `__enter__` 
  and `__exit__` methods of the `Database` class. 
- This design ensures markers are logged only when the class is instantiated via 
  the context manager (`with Database(...)`).
- **Caution:** If additional functionality is added to this script that operates
  outside the context manager, the script markers may not be logged correctly.
  Reevaluate the marker placement in such cases.
"""

import mariadb
from logger import setup_logger, log_marker
import config
from utils import log_event
import textwrap

# Set up logger for this module using the script name
logger = setup_logger(__name__, log_level=config.LOGGING['log_level'], project_id=config.project_id)

# --- SQL Queries ---
FETCH_TITLES_SQL = """
    SELECT tconst, primaryTitle
    FROM title_basics
    WHERE status = 'pending'
    LIMIT %s
"""

UPDATE_STATUS_SQL = """
    UPDATE title_basics
    SET status = 'processing'
    WHERE tconst IN (%s)
"""

UPDATE_BATCH_RESULTS_SQL = """
    UPDATE title_basics
    SET is_foreign = %s, status = %s
    WHERE tconst = %s
"""

class Database:
    """
    Handles connections and interactions with the MariaDB database.
    """
    def __init__(self, db_config):
        self.config = db_config
        self.conn = None

    def __enter__(self):
        # Add script start marker
        log_marker(logger, "SCRIPT START [db_connector.py]")
        try:
            self.conn = mariadb.connect(**self.config)
            logger.info("Database connection established successfully.")
            log_event("Database connection established successfully.")
            return self
        except mariadb.Error as e:
            logger.error(f"Database connection error: {e}")
            log_event(f"Database connection error: {e}", level=logging.ERROR)
            raise

    def __exit__(self, exc_type, exc_value, traceback):
        if self.conn:
            self.conn.close()
            logger.info("Database connection closed.")
            log_event("Database connection closed.")
        # Add script end marker
        log_marker(logger, "SCRIPT END [db_connector.py]")

    def fetch_titles(self, batch_size=None):
        cursor = self.conn.cursor(dictionary=True)
        if batch_size is None:
            batch_size = config.BATCH_SIZE
        try:
            logger.info(f"Fetching {batch_size} titles with status 'pending'.")
            log_event(f"Fetching {batch_size} titles with status 'pending'.")
            cursor.execute(FETCH_TITLES_SQL, (batch_size,))
            titles = cursor.fetchall()
            log_message = "Fetched tconsts:\n" + "\n".join(
                textwrap.fill(", ".join([title['tconst'] for title in titles]), width=120).split("\n")
            )
            logger.debug(log_message)


            if not titles:
                logger.info("No pending titles found for processing.")
                log_event("No pending titles found for processing.")

            if titles:
                titles_to_update = [title['tconst'] for title in titles]
                placeholders = ','.join(['%s'] * len(titles_to_update))
                cursor.execute(UPDATE_STATUS_SQL % placeholders, tuple(titles_to_update))
                self.conn.commit()
                logger.info(f"Updated status to 'processing' for {len(titles_to_update)} titles.")
                log_event(f"Updated status to 'processing' for {len(titles_to_update)} titles.")

            return titles
        except mariadb.Error as e:
            logger.error(f"Database error during fetch_titles: {e}")
            log_event(f"Database error during fetch_titles: {e}", level=logging.ERROR)
            raise
        except Exception as e:
            logger.error(f"Unexpected error during fetch_titles: {e}")
            log_event(f"Unexpected error during fetch_titles: {e}", level=logging.ERROR)
            raise
        finally:
            cursor.close()

    def update_batch_results(self, results):
        cursor = self.conn.cursor()
        try:
            if not results:
                logger.info("No results to update. Skipping database update.")
                log_event("No results to update. Skipping database update.")
                return

            logger.info(f"Updating database with results for {len(results)} titles.")
            log_event(f"Updating database with results for {len(results)} titles.")

            for tconst, is_foreign, status in results:
                cursor.execute(UPDATE_BATCH_RESULTS_SQL, (is_foreign, status, tconst))
            self.conn.commit()

            logger.info("Database updated successfully for all titles in the batch.")
            log_event("Database updated successfully for all titles in the batch.")
        except mariadb.Error as e:
            logger.error(f"Database error during update_batch_results: {e}")
            log_event(f"Database error during update_batch_results: {e}", level=logging.ERROR)
            raise
        except Exception as e:
            logger.error(f"Unexpected error during update_batch_results: {e}")
            log_event(f"Unexpected error during update_batch_results: {e}", level=logging.ERROR)
            raise
        finally:
            cursor.close()
