import logging


class BaseClass:
    def __init__(self):
        self.configure_logger()

    def configure_logger(self):
        self.logger = logging.getLogger(f"{self.__class__.__name__}")
        self.logger.setLevel(logging.INFO)
        formatter = logging.Formatter(
            "%(levelname)s@%(asctime)s: [%(name)s] %(message)s"
        )
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
