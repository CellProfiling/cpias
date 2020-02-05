"""Provide constants for cpias."""
import logging
from pathlib import Path

VERSION = (Path(__file__).parent / "VERSION").read_text().strip()
API_VERSION = "1.0.0"
LOGGER = logging.getLogger(__package__)
