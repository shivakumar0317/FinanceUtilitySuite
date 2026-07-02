"""
Application Logger
"""

import logging
from pathlib import Path

from config import LOG_FOLDER

LOG_FILE = Path(LOG_FOLDER) / "finance_suite.log"


class AppLogger:

    def __init__(self):

        self.logger = logging.getLogger("FinanceUtilitySuite")

        if self.logger.handlers:
            return

        self.logger.setLevel(logging.INFO)

        formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")

        file_handler = logging.FileHandler(LOG_FILE)

        file_handler.setFormatter(formatter)

        self.logger.addHandler(file_handler)

    def info(self, message):

        self.logger.info(message)

    def warning(self, message):

        self.logger.warning(message)

    def error(self, message):

        self.logger.error(message)
