"""Core functionality for Championship Finals processor."""
"""Core business logic for championship placement tracking."""
from .models import ClassInfo
# from .plaza_scraper import plaza
from .debug_logger import print_debug, print_debug2, print_debug3
from .constants import (
    PLAZA_BASE,
    PLAZA_RESULTS,
    KC_WEBSITE,
    HEIGHTS,
    HEIGHT_NAMES,
    REMOVED_WORDS
)

__all__ = [
    'BASE_LINK',
    'PLAZA_BASE', 
    'KC_WEBSITE',
    'HEIGHTS',
    'HEIGHT_NAMES',
    'REMOVED_WORDS',
    'print_debug',
    'print_debug2',
    'print_debug3',
]