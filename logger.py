import logging
import os
import sys
import time

LOGGER = None
STREAM_HANDLER = None
FILE_HANDLER = None
LOG_DIR = "logs"
BASE_FMT = '[%(asctime)s] [PID:%(process)d] ' + \
           '[%(module)s:%(lineno)d] ' + \
           '[%(levelname)s] %(message)s'


def get_logger():
    """Returns Logger"""
    global LOGGER
    if LOGGER is None:
        LOGGER = _create_logger()
    return LOGGER


def _create_logger():
    """Creates logger"""
    level = _get_level_from_env()
    app_lgr = logging.getLogger("APP")
    app_lgr.propagate = False
    app_lgr.setLevel(level)
    app_lgr.addHandler(_get_handler("stream"))
    app_lgr.addHandler(_get_handler("file"))
    return app_lgr


def _get_level_from_env():
    try:
        env = os.environ['BOOK_LOG_LVL'].lower()
    except Exception as e:
        print "Environment variable not found. Please export: ", e
        return 'DEBUG'
    if env == 'dev':
        return 'DEBUG'
    return 'INFO'


def _get_handler(type="stream"):
    """Gets stream, file handlers."""
    global STREAM_HANDLER, FILE_HANDLER
    if type == "stream":
        if STREAM_HANDLER is None:
            STREAM_HANDLER = _create_stream_handler()
        return STREAM_HANDLER
    elif type == "file":
        if FILE_HANDLER is None:
            FILE_HANDLER = _create_file_handler()
        return FILE_HANDLER
    return None


def _create_stream_handler():
    """Creates stream handler that outputs to STDOUT"""
    global STREAM_HANDLER
    STREAM_HANDLER = logging.StreamHandler(sys.stdout)
    log_formatter = logging.Formatter(BASE_FMT)
    logging.Formatter.converter = time.gmtime
    STREAM_HANDLER.setFormatter(log_formatter)
    STREAM_HANDLER.setLevel(logging.DEBUG)
    return STREAM_HANDLER

def _create_file_handler():
    """Creates file handler that outputs to log file"""
    global FILE_HANDLER
    FILE_HANDLER = logging.FileHandler("log.txt")
    log_formatter = logging.Formatter(BASE_FMT)
    logging.Formatter.converter = time.gmtime
    FILE_HANDLER.setFormatter(log_formatter)
    FILE_HANDLER.setLevel(logging.DEBUG)
    return FILE_HANDLER
