import logging

def setup_logging():
    logger = logging.getLogger("movie_rating")
    if logger.hasHandlers():
        # Already configured, skip to avoid duplicates
        return
    logger.setLevel(logging.DEBUG)
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)