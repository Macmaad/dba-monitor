import logging

import logmatic


def get_logger():
    new_logger = logging.getLogger()
    flask_logger = logging.getLogger("werkzeug")
    flask_logger.setLevel(logging.ERROR)
    if new_logger.hasHandlers():
        for hdlr in new_logger.handlers:
            new_logger.removeHandler(hdlr)
    if logmatic:
        handler = logging.StreamHandler()
        log_format = logmatic.JsonFormatter(
            fmt="%(levelname) %(asctime) %(name) %(processName) %(filename) %(funcName) %(lineno) %(module) "
            "%(message)"
        )
        handler.setFormatter(log_format)
    else:
        handler = logging.StreamHandler()
    new_logger.addHandler(handler)
    new_logger.setLevel(logging.INFO)
    return new_logger


logger = get_logger()
