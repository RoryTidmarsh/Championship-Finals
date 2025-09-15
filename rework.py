import requests
from bs4 import BeautifulSoup
import numpy as np
from urllib.parse import urljoin
import pandas as pd
from datetime import datetime
import re
import os
import sys
import difflib

sys.stdout.reconfigure(encoding='utf-8')

print_statements = True
def print_debug(message, *args, **kwargs):
    if print_statements ==True:
        print(message,*args, **kwargs)

base_url = "https://www.agilityplaza.com/results/"

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

def check_show_in_closest(Target_show_name, *args, **kwargs):
    """
    Checks if the target show name exists within the list of closest shows.
    Args:
        Target_show_name (str): The name of the show to search for.
        *args: Variable length argument list to be passed to `find_closest_shows`.
        **kwargs: Arbitrary keyword arguments to be passed to `find_closest_shows`.
    Returns:
        str: The matched show name from the closest shows list.
    Raises:
        ValueError: If the target show name is not found in the closest shows.
    Side Effects:
        Prints a debug message if the target show is found.
    """

    closest_shows_function = find_closest_shows(*args, **kwargs)
    show_names = closest_shows_function["Show Name"].to_list()
    match = next((name for name in show_names if name.strip().lower() == Target_show_name.strip().lower()), None)
    if not match:
        raise ValueError(f"Target show '{Target_show_name}' not found in closest shows.")
    else:
        print_debug(f"Target show '{match}' found in closest shows.")
        return match


def is_close_match(target, candidate, threshold=0.7):
    """
    Determines whether two strings are considered a close match based on several criteria:
    abbreviation equivalence, exact match, substring match, and fuzzy matching.
    Args:
        target (str): The first string to compare.
        candidate (str): The second string to compare.
        threshold (float, optional): The minimum similarity ratio (between 0 and 1) for fuzzy matching.
            Defaults to 0.7.
    Returns:
        bool: True if the strings are considered a close match, False otherwise.
    Matching criteria:
        - Abbreviation match: Checks if either string matches a known abbreviation of the other.
        - Exact match: Checks if the normalized strings are identical.
        - Substring match: Checks if one string is a substring of the other.
        - Fuzzy match: Uses difflib.SequenceMatcher to compare similarity ratio.
    """

    target_norm = target.strip().lower()
    candidate_norm = candidate.strip().lower()
    # Check for abbreviation match
    abbreviations = {
        "kennel club international agility festival": "kciaf",
        "dogs in need agility society": "dinas",
        # Add more abbreviations as needed
    }
    target_abbr = abbreviations.get(target_norm, None)
    candidate_abbr = abbreviations.get(candidate_norm, None)
    if target_abbr and (target_abbr == candidate_norm or target_abbr == candidate_abbr):
        return True
    if candidate_abbr and (candidate_abbr == target_norm or candidate_abbr == target_abbr):
        return True
        # Exact match
    if target_norm == candidate_norm:
        return True
    # Substring match
    if target_norm in candidate_norm or candidate_norm in target_norm:
        return True
    # Fuzzy match
    ratio = difflib.SequenceMatcher(None, target_norm, candidate_norm).ratio()
    return ratio >= threshold

def find_show_url(show_name,*args, **kwargs):
    """
    Find the URL of a show given its name.

        Args:
        show_name (str): Name of the show to find.

    Returns:
        str: URL of the show if found, otherwise None.
    """
    # Finding the date of the target show
    if 'num_shows' in args or kwargs:
        print("num_shows found in args or kwargs")
    closest_shows_df = find_closest_shows(*args, **kwargs)
    show_name = check_show_in_closest(show_name, *args, **kwargs)
    show_date = closest_shows_df.loc[closest_shows_df['Show Name'] == show_name, 'Date'].values[0]
    show_year, show_month, show_day = pd.to_datetime(show_date).year, pd.to_datetime(show_date).month, pd.to_datetime(show_date).day
    print_debug(f"Searching for show '{show_name}' on date {show_year}-{show_month:02d}-{show_day:02d}")

    month_map = {1: "January", 2: "February", 3: "March", 4: "April",
                5: "May", 6: "June", 7: "July", 8: "August",
                9: "September", 10: "October", 11: "November", 12: "December"}
    
    response = requests.get(base_url)
    soup = BeautifulSoup(response.content, 'html.parser')

    # Finding the month section
    target_month = month_map[show_month]
    monthly_soup = soup.find_all('thead')
    for month in monthly_soup:
        if target_month in month.get_text():
            print_debug(f"Found month section for {target_month}.")
            break

    # Finding the specific show within the month
    show_rows = month.find_next_siblings('tr')
    # Search for exact match first, then close match
    # Normalize abbreviations for matching
    abbreviations = {
        "kennel club international agility festival": "kciaf",
        "dogs in need agility society": "dinas",
        # Add more abbreviations as needed
    }
    def normalize(name):
        name = name.strip().lower()
        return abbreviations.get(name, name)

    target_norm = normalize(show_name)
    # First pass: exact and abbreviation match
    for row in show_rows:
        columns = row.find_all('td')
        if len(columns) >= 2:
            row_name = columns[1].get_text(strip=True)
            row_norm = normalize(row_name)
            if target_norm == row_norm:
                print_debug(f"Found exact/abbreviation match: {row_name}")
                link = row.get('data-href')
                if link:
                    print_debug(f"Found link: {link}")
                    return urljoin(base_url, link)
                else:
                    print_debug("No link found in data-href.")
                    break

    # Second pass: substring and fuzzy match
    for row in show_rows:
        columns = row.find_all('td')
        if len(columns) >= 2:
            row_name = columns[1].get_text(strip=True)
            row_norm = normalize(row_name)
            # Substring or fuzzy match
            if (target_norm in row_norm) or (row_norm in target_norm) or is_close_match(show_name, row_name):
                print_debug(f"Found close match: {row_name}")
                link = row.get('data-href')
                if link:
                    print_debug(f"Found link: {link}")
                    return urljoin(base_url, link)
                else:
                    print_debug("No link found in data-href.")
                    break

    # If no show found, raise an error
    raise ValueError(f"Show name '{show_name}' not found in the month section on Agility Plaza.")

Target_show_name = "North Derbyshire Dog Agility Club"
print(find_show_url("North Derbyshire Dog Agility Club", num_shows=30))

# check_show_in_closest("Agility Club", num_shows=30)