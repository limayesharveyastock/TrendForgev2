"""
TrendForge v2
Configuration Service
"""

from pathlib import Path
import json


class ConfigService:

    CONFIG_DIR = Path("config")

    @classmethod
    def load(cls, filename):

        path = cls.CONFIG_DIR / filename

        with open(path, "r", encoding="utf-8") as f:

            return json.load(f)

    @classmethod
    def save(cls, filename, data):

        path = cls.CONFIG_DIR / filename

        with open(path, "w", encoding="utf-8") as f:

            json.dump(
                data,
                f,
                indent=4
            )