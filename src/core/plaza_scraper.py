"""Webscraper for agilityplaza.com to find show URLs and championship classes."""
import requests
import numpy as np
from bs4 import BeautifulSoup
from src.core.models import ClassInfo
from src.core.debug_logger import print_debug, print_debug2, print_debug3
from src.core.constants import *
from src.core.KC_ShowProcesser import is_close_match
# from src.core.KC_ShowProcesser import find_closest_shows, check_show_in_closest, is_close_match
from urllib.parse import urljoin
import pandas as pd
from .constants import PLAZA_RESULTS as base_url

def find_show_url(show_name, show_date):
    """
    Find the URL of a show given its name.

        Args:
        show_name (str): Name of the show to find.
        show_date (str/pd.Timestamp/np.datetime64): Date of the show to find.

    Returns:
        str: URL of the show if found, otherwise None.
    """
    # Type Checking
    assert isinstance(show_name, str), "show_name must be a string."
    assert isinstance(show_date, (str, pd.Timestamp, pd.DatetimeTZDtype, np.datetime64)), "show_date must be a string or pandas Timestamp."
    # closest_shows_df = find_closest_shows(*args, **kwargs)
    # show_name = check_show_in_closest(show_name, *args, **kwargs)
    # show_date = closest_shows_df.loc[closest_shows_df['Show Name'] == show_name, 'Date'].values[0]

    # Extract year, month, day from show_date
    show_year, show_month, show_day = pd.to_datetime(show_date).year, pd.to_datetime(show_date).month, pd.to_datetime(show_date).day
    print_debug(f"Searching for show '{show_name}' on date {show_year}-{show_month:02d}-{show_day:02d}")

    month_map = {1: "January", 2: "February", 3: "March", 4: "April",
                5: "May", 6: "June", 7: "July", 8: "August",
                9: "September", 10: "October", 11: "November", 12: "December"}
    
    # Fetch the main results page
    search_URL = base_url + str(show_year)
    print_debug(f"Fetching Agility Plaza page for year {show_year} from URL: {search_URL}")
    
    soup = get_soup(search_URL)

    # Finding the month section
    target_month = month_map[show_month]
    monthly_soup = soup.find_all('thead')
    found_month = False
    for i, month in enumerate(monthly_soup):
        if target_month in month.get_text():
            print_debug(f"Found month section for {target_month}.")
            found_month = True
            break
    if not found_month:
        raise ValueError(f"Month '{target_month}' not found on Agility Plaza for year {show_year}.")

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
                            jumping_class.running_orders_url = "https://www.agilityplaza.com" + link
                            
                        elif "Agility" in text:
                            agility_class.class_number = class_number
                            agility_class.class_type = class_type
                            agility_class.running_orders_url = "https://www.agilityplaza.com" + link
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
                    link = "https://www.agilityplaza.com" + a.get('href')

                    # Store information in the class object
                    jumping_class.class_number,_,_,jumping_class.class_type = name.split(" ")
                    jumping_class.results_url = link

                    found_classes += 1
                    print_debug2(f"Found Championship Jumping class: {name}, link: {link}")

                elif "Championship Agility" in text and height.lower() in text.lower():
                    name = text
                    link = "https://www.agilityplaza.com" + a.get('href')

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

def find_champClass_fromIDs(agilityID, jumpingID):
    """Find championship classes based on their IDs.
    
    Args:
        agilityID (str/int): Agility class ID, must be a 10-digit numeric string or integer.
        jumpingID (str/int): Jumping class ID, must be a 10-digit numeric string or integer.

    Returns:
        tuple: A tuple containing two ClassInfo objects (agility_class, jumping_class).
    """
    assert str(agilityID).isdigit(), "agilityID must be numeric."
    assert str(jumpingID).isdigit(), "jumpingID must be numeric."
    assert len(str(agilityID)) == 10, "agilityID must be 10 digits."
    assert len(str(jumpingID)) == 10, "jumpingID must be 10 digits."

    # Create URL from digits
    agility_url = os.path.join(PLAZA_BASE, str(agilityID), "results/")
    jumping_url = os.path.join(PLAZA_BASE, str(jumpingID), "results/")

    return {agilityID: agility_url, jumpingID: jumping_url}

def extract_class_id(class_link):
    """Extracts the class ID from a given class link.

    Args:
        class_link (str): The URL of the class results page.

    Returns:
        str: The extracted class ID.
    """
    assert isinstance(class_link, str), "class_link must be a string."
    parts = class_link.strip('/').split('/')
    
    assert len(parts) == 6, "class_link format is incorrect."
    assert parts[2] == "www.agilityplaza.com" or "www.agilityplaza.co.uk", "class_link must be from agilityplaza.com."
    
    ID = parts[4]
    assert ID.isdigit() and len(ID) == 10, "Extracted ID is not a valid 10-digit numeric string."
    
    return ID

def get_soup(url):
    """Fetches the content of a URL and returns a BeautifulSoup object."""
    response = requests.get(url)
    if response.status_code != 200:
        raise ConnectionError(f"Failed to fetch URL: {url}. Status code: {response.status_code}")
    show_soup = BeautifulSoup(response.content, 'html.parser')
    return show_soup

if __name__ == "__main__":
    from .KC_ShowProcesser import find_closest_shows, check_show_in_closest
    test_show_name = "North Derbyshire Dog Agility Club"
    closest_shows_df = find_closest_shows(days_ahead=0, num_shows=30)
    try:
        matched_show, matched_showDate = check_show_in_closest(test_show_name, closest_shows_df)
    except ValueError as e:
        raise ValueError(str(e))
    
    print("\n==== Testing Show URL Finder ====")
    try:
        show_url = find_show_url(test_show_name, matched_showDate)
        print_debug(f"Show URL for '{test_show_name}': {show_url}")
    except ValueError as e:
        raise ValueError(str(e))

    print("\n==== Testing Championship Class Finder ====")
    height = "Lge"

    # Fetch the show page
    show_soup = get_soup(show_url)
    try:
        agility_class, jumping_class = find_champ_classes(show_soup, height)
        print_debug(f"Agility Class: {agility_class}")
        print_debug(f"Jumping Class: {jumping_class}")
    except ValueError as e:
        raise ValueError(str(e))