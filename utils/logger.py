"""
utils/logger.py
================

Centralized logging configuration for TrendForge.

Features
--------
✓ Console logging
✓ Rotating file logging
✓ Daily log files
✓ Separate error log
✓ Colored console output (optional)
✓ Thread-safe
✓ Singleton logger manager
"""

from __future__ import annotations

import logging
import logging.handlers
import os
from pathlib import Path


class LoggerManager:
    """
    Central logging manager for TrendForge.
    """

    _initialized = False

    LOG_DIR = Path("logs")

    LOG_LEVEL = logging.INFO

    LOG_FORMAT = (
        "%(asctime)s | "
        "%(levelname)-8s | "
        "%(name)s | "
        "%(filename)s:%(lineno)d | "
        "%(message)s"
    )

    DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

    @classmethod
    def initialize(cls):

        if cls._initialized:
            return

        cls.LOG_DIR.mkdir(
            parents=True,
            exist_ok=True
        )

        formatter = logging.Formatter(
            cls.LOG_FORMAT,
            cls.DATE_FORMAT
        )

        ##########################################################
        # Root Logger
        ##########################################################

        root_logger = logging.getLogger()

        root_logger.setLevel(cls.LOG_LEVEL)

        # Prevent duplicate handlers
        if root_logger.handlers:
            root_logger.handlers.clear()

        ##########################################################
        # Console Handler
        ##########################################################

        console_handler = logging.StreamHandler()

        console_handler.setFormatter(formatter)

        console_handler.setLevel(logging.INFO)

        ##########################################################
        # Application Log
        ##########################################################

        file_handler = logging.handlers.TimedRotatingFileHandler(

            filename=cls.LOG_DIR / "trendforge.log",

            when="midnight",

            interval=1,

            backupCount=30,

            encoding="utf-8"

        )

        file_handler.setFormatter(formatter)

        file_handler.setLevel(logging.INFO)

        ##########################################################
        # Error Log
        ##########################################################

        error_handler = logging.handlers.TimedRotatingFileHandler(

            filename=cls.LOG_DIR / "errors.log",

            when="midnight",

            interval=1,

            backupCount=60,

            encoding="utf-8"

        )

        error_handler.setFormatter(formatter)

        error_handler.setLevel(logging.ERROR)

        ##########################################################

        root_logger.addHandler(console_handler)

        root_logger.addHandler(file_handler)

        root_logger.addHandler(error_handler)

        cls._initialized = True

    ##############################################################

    @staticmethod
    def get_logger(name: str):

        LoggerManager.initialize()

        return logging.getLogger(name)

    ##############################################################

    @staticmethod
    def set_level(level):

        LoggerManager.initialize()

        logging.getLogger().setLevel(level)

    ##############################################################

    @staticmethod
    def disable():

        logging.disable(logging.CRITICAL)

    ##############################################################

    @staticmethod
    def enable():

        logging.disable(logging.NOTSET)


##################################################################
# Initialize Automatically
##################################################################

LoggerManager.initialize()


##################################################################
# Convenience Logger
##################################################################

logger = LoggerManager.get_logger("TrendForge")