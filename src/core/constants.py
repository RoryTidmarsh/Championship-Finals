"""Constants for the core championship placement module."""

# Agility Plaza URLs
PLAZA_RESULTS = "https://www.agilityplaza.co.uk/results/"
PLAZA_BASE = "https://www.agilityplaza.co.uk"
KC_WEBSITE = "https://www.thekennelclub.org.uk/events-and-activities/agility/already-competing-in-agility/qualifying-shows-for-the-kennel-club-events/"

# Height categories
HEIGHTS = ["Sml", "Med", "Int", "Lge"]
HEIGHT_NAMES = {"Sml": "Small", "Med": "Medium", "Int": "Intermediate", "Lge": "Large"}

# Column headings for results tables
COLUMN_HEADINGS = ["place1", "place2", "posh names", "name", "type", "faults", "time"]

# Words to remove when cleaning show names
REMOVED_WORDS = [
    "DTC",
    "Dog",
    "Training",
    "Society",
    "and",
    "&",
    "Club",
    "in",
    "In",
    "Obedience",
    "(Dorset)",
    "District",
    "(Lancs)",
    "Show",
    "Championship",
    "agility",
]

# Timing
REFRESH_INTERVAL = 120  # seconds
