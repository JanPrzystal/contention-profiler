import logging

LOGGER_NAME = __name__ #"experiment_logger"
logger = logging.getLogger(LOGGER_NAME)

def setup_logging():
    global logger
    logger.setLevel(logging.INFO)

    fmt = logging.Formatter("[%(levelname)s] %(message)s")

    # log to file
    fh = logging.FileHandler("experiment_results/log.log")
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(fmt)

    # log to console
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO) 
    ch.setFormatter(fmt)

    logger.addHandler(fh)
    logger.addHandler(ch)

def log(message: str, level=logging.INFO):
    global logger
    if level == logging.DEBUG:
        logger.debug(message)
    elif level == logging.INFO:
        logger.info(message)
    elif level == logging.WARNING:
        logger.warning(message)
    elif level == logging.ERROR:
        logger.error(message)
    elif level == logging.CRITICAL:
        logger.critical(message)