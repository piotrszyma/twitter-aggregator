import logging


def configure_logger(debug: bool) -> logging.Logger:
    logger = logging.getLogger("twitter_aggregator")
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    if debug:
        logger.setLevel(logging.DEBUG)
    return logger
