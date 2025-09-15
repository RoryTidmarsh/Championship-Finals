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
from NorthDerbySaves.running_orders import read_from_file

sys.stdout.reconfigure(encoding='utf-8')

print_statements = False
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
# print(find_show_url("North Derbyshire Dog Agility Club", num_shows=30))

"""Now, use saved HTML from a running competition: North Derbyshire show
The files we have in `NorthDerbySaves` are:
 - NorthDerbyRunningOrders_LgeJmp.html: Running orders of large jump, 2nd champ round
 - NorhtDerbyShow_FirstClass.html: HTML of results page while only large agility is shown. This has results link to the first class and links to both running orders.
 - NorthDerbyShow_SecondClass.html: HTML file of the results page of ND show while the second round of champ is running. 
 - NorthDerbyShow_LgeAg_complete.html: HTML of large champ agility results (class finished)
 - NorthDerbyShow_LgeJmp_incomplete.html: HTML of large champ jumping results (class in progress).

 The 2 results files should be accessable from the `NorthDerbyShow_SecondClass.hrml` file. So start the code with that.
"""
print_statements2 = False
def print_debug2(message, *args, **kwargs):
    if print_statements2 ==True:
        print(message,*args, **kwargs)
# def read_from_file(filename="NorthDerbyShow.txt"):
#     with open(filename, "r", encoding="utf-8") as f:      
#         html = f.read()
#     soup = BeautifulSoup(html, 'html.parser')
#     return soup

## Actual soup from the web, comment out when using saved file.
# response = requests.get(find_show_url(Target_show_name, num_shows=10))
# soup = BeautifulSoup(response.content, 'html.parser')

simulation_soup = read_from_file("NorthDerbySaves\\NorthDerbyShow_SecondClass.html")


class ClassInfo:
    def __init__(self, class_type, class_number = None, order = 0, running_orders_url = None, results_url = None):
        self.class_type = class_type
        # self.status = status
        self.order = order
        self.running_orders_url = running_orders_url
        self.results_url = results_url
        self.class_number = class_number
        self.status = None  # e.g., "completed", "in progress", "not started"
        self.order_hierarchy = {"first": 0, "second": 1, "same state": 2}

    def __repr__(self):
        return (f"ShowClassInfo(class_type={self.class_type}, status={self.status}, "
                f"order={self.order}, running_orders_url={self.running_orders_url}, "
                f"results_url={self.results_url}, "
                f"class_number={self.class_number})")
    
    def update_status(self):
        if self.running_orders_url and self.results_url:
            self.status = 'in progress'
        elif self.results_url and not self.running_orders_url:
            self.status = 'completed'
        elif self.running_orders_url and not self.results_url:
            self.status = 'not started'
    def update_order(self, other):
        status_hierarchy = {"completed": 0, "in progress": 1, "not started": 2}
        if status_hierarchy[self.status] < status_hierarchy[other.status]:
            self.order = 0
            other.order = 1
        elif status_hierarchy[self.status] > status_hierarchy[other.status]:
            self.order = 1
            other.order = 0
        else:
            self.order = 2
            other.order = 2
            
def find_champ_classes(soup, height):
    """
    Finds all championship classes in the given BeautifulSoup object.

    Args:
        soup (BeautifulSoup): The BeautifulSoup object to search.
        height (str): The height category to filter classes by (e.g., 'Lge', 'Int', 'Med', 'Sml').
    
    Returns:
        tuple: A tuple containing two ClassInfo objects (agility_class, jumping_class)."""

    height_list = ['lge', 'int', 'med', 'sml']
    if height.lower() not in height_list:
        raise ValueError(f"Height must be one of these: {height_list}.")

    # Headers on Plaza
    headers = soup.find_all('div', class_='card-header')

    agility_class = ClassInfo("agility")
    jumping_class = ClassInfo("jumping")
    found_classes = 0
    # Find the running orders if availiable
    for header in headers:
        header_text = header.get_text(strip=True).lower()

        # Look for running orders
        if header_text == "running orders":
            card = header.find_parent('div', class_='card')
            if card:
                for span in card.find_all('span'):
                    text = span.get_text(strip=True)
                    print_debug2(f"Found running orders text: {text}")
                    if "championship" in text.lower() and height.lower() in text.lower():
                        # Store the class number and type
                        class_number,_,_,class_type = text.split(" ")

                        # Get the URL
                        link_tag = span.find_parent('a')
                        if link_tag and link_tag.has_attr('href'):
                            link = link_tag['href']
                        else:
                            raise ValueError(f"No link found for running orders of {text}")
                        if "Jumping" in text:
                            jumping_class.class_number = class_number
                            jumping_class.class_type = class_type
                            jumping_class.running_orders_url = "https://agilityplaza.com" + link
                            
                        elif "Agility" in text:
                            agility_class.class_number = class_number
                            agility_class.class_type = class_type
                            agility_class.running_orders_url = "https://agilityplaza.com" + link
                        found_classes += 1
                        print_debug2(f"Class number: {class_number}, Class type: {class_type}, link: {link}")
                        
        else:
            # Each card block contains a table for the days results
            card_block = header.find_next_sibling('div', class_='card-block')
            if card_block:
                print_debug2(f"Found card block for header: {header_text}")
            else:
                print_debug2(f"No card block found for header: {header_text}")
                continue

            for a in card_block.find_all('a'):
                text = a.get_text(strip=True)
                if "Championship Jumping" in text and height.lower() in text.lower():
                    name = text
                    link = "https://agilityplaza.com" + a.get('href')

                    # Store information in the class object
                    jumping_class.class_number,_,_,jumping_class.class_type = name.split(" ")
                    jumping_class.results_url = link

                    found_classes += 1
                    print_debug2(f"Found Championship Jumping class: {name}, link: {link}")

                elif "Championship Agility" in text and height.lower() in text.lower():
                    name = text
                    link = "https://agilityplaza.com" + a.get('href')

                    # Store information in the class object
                    agility_class.class_number,_,_,agility_class.class_type = name.split(" ")
                    agility_class.results_url = link

                    found_classes += 1
                    print_debug2(f"Found Championship Agility class: {name}, link: {link}")
                    
    if found_classes == 0:
        raise ValueError(f"No championship class found for height '{height.capitalize()}'.")
    # Update status and order
    agility_class.update_status()
    jumping_class.update_status()
    agility_class.update_order(jumping_class)
    print_debug2(f"Agility Class Info: {agility_class}")
    print_debug2(f"Jumping Class Info: {jumping_class}")        

    return agility_class, jumping_class

print(find_champ_classes(simulation_soup, 'int'))