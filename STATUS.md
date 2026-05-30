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
|-- /frontend - directory with frontend code for the web application (React)
|
|-- /src
|   |-- /api - directory with API related code
|       |-- __init__.py - init file for the api module
|       |-- routes.py - module defining the API routes for the FastAPI app
|       |-- models.py - module defining the data models for the API
|       |-- handlers.py - module defining the request handlers for the API endpoints
|       |-- session.py - module for managing API sessions and state *unused*
|
|   |-- /core - core package with all the main functionality of the project
|       |-- __init__.py - init file for the core module
|       |-- KC_ShowProcesser.py - module to process KC show data, find closest shows, and check for matches
|       |-- plaza_scraper.py - module to scrape Plaza website for show class URLs
|       |-- plaza_R&RO.py - module to import and process results and running orders from Plaza
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

All backend logic for finding championship shows, scraping Plaza for class URLs, importing results and running orders, and combining results has been reworked into a modular structure under `src/core/`. The main functionality is divided into separate modules for better organization and maintainability.

- `src/core/`, package currently contains modules to find the URLs and status of each championship show. The functionality of modules & flow of processing is as follows:
  1. `KC_ShowProcesser.py`: processes KC show dataset, finds closest shows & checks for the input show in the data. _use this to find if the show exists as a championship show & find the date of the show_
  2. `plaza_scraper.py`: scrapes Plaza/results website to find class URLs for the specified show. _use this to get the URLs for the input show_
  3. `plaza_R&RO.py`: uses the class URL from the module above to import results and running orders into DataFrames. _use this to get the results and running orders for the input show, output as `ClassInfo` from `models.py`_
  4. `models.py`: defines:
     - `ClassInfo` data model to hold class information, results, and running orders.
     - `Finals` data model to combine results from 2 classes and determine overall standings.
     - `pairingInfo` data model to hold pairing information for competitors. **_WIP_**
- Testing code has been added to the `if __name__ == "__main__":` sections of each module to demonstrate functionality. **_Need to convert these into proper unit tests later._**

### Next Steps

1. Add module for calculations of what each competitor that is yet to run needs to qualify for the championship finals based on current results.
   - Read Running Orders of live class
   - See if competitor has run yet, if not continue
   - load score from first round
   - Calc what they need to get top 20, score returned should be time and faults or 1st place if that got eliminated in round 1
2. unit testing: convert the test code in the `if __name__ == "__main__":` sections into proper unit tests using a testing framework like `unittest` or `pytest`.
3. integration: create an integration script that ties together the modules to process a show from start to finish.
4. add the following for webapp response status

```
response = requests.get(show_class.results_url)
   response.raise_for_status()
```

## Website Structure

- "`/`" - Home page with show input form for users to select show name and height category. (optional URL input form to be kept). Give a dropdown choice of shows listing from the most recent shows in dataset, but allow some future ones if they are close enough.
- "`/combined-results`" - Page to display combined results of the 2 rounds and the satus of each round (completed/in progress/not started). Show the combined results table with appropriate formatting. This page needs to have the parameters passed in the URL or session to know which show and height category to display, for example: `/combined-results?agility=0123456789&jumping=0987654321&height=Lge`. Where the agility and jumping parameters are the class IDs from Plaza URLs. **\*new parameters** purpose is to allow sharing of links to specific show results and refresh of page.\*
- "`/requirements`", Page to display what each competitior needs to make the championship finals based on current results, must have URL parameters. Show a table with competitors and their required scores.
  - This will need some logic calculations to determine what each competitor needs based on their current scores and the cutoff for the finals. This does not exist yet.
