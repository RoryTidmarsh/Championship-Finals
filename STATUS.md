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
|-- rework.py - main script for the reworked version of the project
|-- csv files - CSV files for the name and dates of the champtionship shows
|-- find_champ_show_db.py - script to find championship shows from KC website and to return the csv files above (not reworked yet)
|-- requirements.txt - list of Python dependencies for the project
```

Repository and `rework.py` needs to be restructured to create a module with the html reading files, test reading files and the flask app. These need to be in their own respective directories with `__init__.py` files.
