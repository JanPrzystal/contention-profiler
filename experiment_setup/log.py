import logging
from pathlib import Path
import config
import os

LOGGER_NAME = __name__
DEBUG = logging.DEBUG
INFO = logging.INFO
WARNING = logging.WARNING
ERROR = logging.ERROR

logger = logging.getLogger(LOGGER_NAME)

def setup_logging(level=logging.INFO):
    global logger
    # remove/close any existing handlers to avoid writing to deleted files
    for h in list(logger.handlers):
        try:
            logger.removeHandler(h)
            h.flush()
            h.close()
        except Exception:
            pass

    logger.setLevel(level)

    fmt = logging.Formatter("[%(levelname)s] %(message)s")

    # ensure results directory exists before creating file handler
    Path(config.RESULTS_DIR).mkdir(parents=True, exist_ok=True)

    # log to file inside the configured results directory with line buffering
    # Open file with buffering=1 (line buffering) to flush on each newline
    log_file = open(f"{config.RESULTS_DIR}/log.log", "a", buffering=1)
    fh = logging.StreamHandler(log_file)
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(fmt)

    # log to console
    ch = logging.StreamHandler()
    ch.setLevel(level)
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

    for handler in logger.handlers:
        if hasattr(handler, 'stream') and hasattr(handler.stream, 'fileno'):
            try:
                os.fsync(handler.stream.fileno())
            except (OSError, AttributeError):
                pass