import requests
from bs4 import BeautifulSoup
import numpy as np
from urllib.parse import urljoin
import pandas as pd
from datetime import datetime
import re
import os
print_statements = True
def print_debug(message, *args, **kwargs):
    if print_statements ==True:
        print(message,*args, **kwargs)

def find_closest_shows(champ_shows_filepath = "champ shows.csv", days_ahead=0, num_shows=5):
    """
    Find the closest championship shows to a given date.

    Args:
        champ_shows_filepath (str, optional): Filepath to the a csv file storing information on the shows. Defaults to "Champ shows.csv".
        days_ahead (int, optional): How many days to vary from the current date. Defaults to 0.
        num_shows (int, optional): shows to display in the list. Defaults to 5.

    Returns:
        Pandas Dataframe: Dataframe of the closest shows with columns added columns 'timedelta', and 'is_future'.
    """
    tomorrow_date = datetime.now().date() + pd.Timedelta(days=days_ahead)
    champ_shows_df = pd.read_csv(champ_shows_filepath, parse_dates=['Date'])
    champ_shows_df['timedelta'] = (champ_shows_df['Date'].dt.date - tomorrow_date).abs()
    champ_shows_df['is_future'] = champ_shows_df['Date'].dt.date > tomorrow_date
    champ_shows_df = champ_shows_df.sort_values(by='timedelta')
    champ_shows_df = champ_shows_df.head(num_shows).sort_values(by=['is_future', 'Date'], ascending=[True, False])
    print_debug("Closest Shows from Function:\n", champ_shows_df[["Show Name", "Date", "timedelta", "is_future"]])
    return champ_shows_df

closest_shows_function = find_closest_shows(days_ahead=0)


Target_show_name = "North Derbyshire Dog Agility Club"
if Target_show_name not in closest_shows_function["Show Name"].to_list():
    raise ValueError(f"Target show '{Target_show_name}' not found in closest shows.")
else:
    print_debug(f"Target show '{Target_show_name}' found in closest shows.")