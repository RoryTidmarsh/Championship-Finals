# STATUS OF THE BRANCH

### Repo structure

```
/Championship-Finals
|-- /NorthDerbySaves - directory with HTML saves of a live show, for testing. contains show html files and class files (agility completed, jumping in progress)
|
|-- /Old structure - directory with old structure of the project. app GUI and app.py of the old website
|   |-- /static - directory with static files (CSS, JS, images) for the Flask app
|
|-- /templates - directory with HTML templates for the Flask app
|
|-- rework.py - main script for the reworked version of the project *has been separated into a new module structure `src/core`*
|-- /src
|   |-- /core - core module with all the main functionality of the project
|       |-- __init__.py - init file for the core module
|       |-- KC_ShowProcesser.py - module to process KC show data, find closest shows, and check for matches
|       |-- plaza_scraper.py - module to scrape Plaza website for show class URLs
|       |-- plaza_resultsRunningOrder.py - module to import and process results and running orders from Plaza
|       |-- models.py - module defining data models used in the project (ClassInfo)
|       |-- debug_logger.py - module for debug logging functionality
|       |-- constants.py - module defining constants used in the project
|
|-- csv files - CSV files for the name and dates of the champtionship shows
|-- find_champ_show_db.py - script to find championship shows from KC website and to return the csv files above *(not reworked yet & doesn't work well)*. Issue is that the KC website does not use the same naming conventions as Plaza, so matching is difficult. Much easier to do this manually for the yearly update.
|-- requirements.txt - list of Python dependencies for the project
|-- runtime.txt & .python-version - files specifying the Python runtime version for deployment (not sure why both are needed)
|-- README.md - readme file for the project
|-- STATUS.md - this status file
|-- .gitignore - git ignore file
```

### Current Status

- `rework.py` has been split into a new module structure under `src/core/`. The code has been refactored to improve readability and maintainability.
- `src/core/` functionality & flow:
    - `KC_ShowProcesser.py`: processes KC show dataset, finds closest shows & checks for the input show in the data. *use this to find if the show exists as a championship show & find the date of the show*
    - `plaza_scraper.py`: scrapes Plaza/results website to find class URLs for the specified show. *use this to get the URLs for the input show*
    - `plaza_resultsRunningOrder.py`: uses the class URL from the module above to import results and running orders into DataFrames. *use this to get the results and running orders for the input show, output as `ClassInfo` from `models.py`*
    - `models.py`: defines the `ClassInfo` data model to hold class information, results, and running orders.


