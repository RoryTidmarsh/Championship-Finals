"""Module for importing and parsing competition results and running order pages from agilityplaza.com. Returning pandas DataFrames of the main tables."""
import requests
from bs4 import BeautifulSoup
import os
from .debug_logger import *
from .models import ClassInfo
from urllib.parse import urljoin
import pandas as pd
from .constants import PLAZA_RESULTS as base_url

def read_from_file(filename="NorthDerbyShow.txt"):
    with open(filename, "r", encoding="utf-8") as f:      
        html = f.read()
    soup = BeautifulSoup(html, 'html.parser')
    return soup

def process_eliminations(eliminations_text):
    """Process elimination text into a list of eliminated competitors without their prior faults."""
    eliminations = []
    
    # Split by comma, but need to handle cases where commas appear inside parentheses
    current_entry = ""
    paren_depth = 0
    
    for char in eliminations_text:
        if char == '(':
            paren_depth += 1
            current_entry += char
        elif char == ')':
            paren_depth -= 1
            current_entry += char
        elif char == ',' and paren_depth == 0:
            # This is a separator comma, not inside parentheses
            if current_entry.strip():
                eliminations.append(current_entry.strip())
            current_entry = ""
        else:
            current_entry += char
    
    # Don't forget the last entry
    if current_entry.strip():
        eliminations.append(current_entry.strip())
    
    # Remove fault information in parentheses
    eliminations = [entry.split(" (")[0].strip() for entry in eliminations]
    return eliminations

def process_class_df(df):
    headers = df.columns.tolist()
    wanted_headers = ['Rank', 'Place (mobile)', 'KC names', 'Name', 'Run Data', 'Faults', 'Time']
    status = "in progress"
    if "Rank" not in headers and "Place" in headers:
        # Replace headers to standard ones
        df.columns = wanted_headers
        status = "omplete"

    # Remove any non numbers from Rank column
    df['Rank'] = df['Rank'].astype(str).str.extract('(\d+)').astype(int)
    df['Place (mobile)'] = df['Place (mobile)'].astype(str).str.extract('(\d+)').astype(int)
    
    return df, status


def import_results(show_class, simulation=False):
    """
    Imports and parses competition results from a web page or local file.
    
    Args:
        show_class (ClassInfo): The ClassInfo object containing the results URL and class type.
        simulation (bool): If True, reads from local HTML files instead of web scraping.
    
    Returns:
        tuple: (DataFrame, list) containing:
            - df: pandas DataFrame with competition results (or None if no results_url)
            - eliminations: list of eliminated competitors (or None if no results_url)
        Returns (None, None) if no results URL is provided.
    
    Raises:
        ValueError: If show_class is invalid, class_type unsupported, or HTML structure unexpected
        requests.RequestException: If web request fails
        FileNotFoundError: If simulation file is not found
        RuntimeError: If table parsing fails unexpectedly
    """
    # Validate input parameters
    if not show_class:
        raise ValueError("show_class parameter cannot be None")
    
    if not hasattr(show_class, 'results_url'):
        raise ValueError("show_class must have a results_url attribute")
    
    # Handle case where results_url is None - return None, None gracefully
    if show_class.results_url is None:
        print_debug3(f"No results URL provided from {show_class.class_type} - returning None, None. Class status: {show_class.status}")
        return None, None
    
    # Check for empty string URL
    if not show_class.results_url.strip():
        raise ValueError("show_class results_url cannot be empty string")
    
    if not hasattr(show_class, 'class_type') or not show_class.class_type:
        raise ValueError("show_class must have a valid class_type attribute")
    
    soup = None
    
    if not simulation:
        # Fetch results from web
        print_debug3(f"Fetching results from URL: {show_class.results_url}")
        try:
            response = requests.get(show_class.results_url)
            response.raise_for_status()  # Raises requests.HTTPError for bad status codes
            soup = BeautifulSoup(response.content, 'html.parser')
        except requests.RequestException as e:
            raise requests.RequestException(f"Failed to fetch results from {show_class.results_url}: {e}")
    else:
        # Load results from local simulation files
        print_debug3(f"Loading simulation data for class type: {show_class.class_type}")
        
        if show_class.class_type.lower() == "agility":
            agility_url = os.path.join("NorthDerbySaves", "NorthDerbyShow_LgeAg_compeleted.html")
            try:
                simulation_soup = read_from_file(agility_url)
            except FileNotFoundError:
                raise FileNotFoundError(f"Simulation file '{agility_url}' not found")
        elif show_class.class_type.lower() == "jumping":
            jumping_url = os.path.join("NorthDerbySaves", "NorthDerbyShow_LgeJmp_incomplete.html")
            try:
                simulation_soup = read_from_file(jumping_url)
            except FileNotFoundError:
                raise FileNotFoundError(f"Simulation file '{jumping_url}' not found")
        else:
            raise ValueError(f"Unsupported class type for simulation: '{show_class.class_type}'. "
                           f"Supported types are: 'agility', 'jumping'")
        
        soup = simulation_soup

    if not soup:
        raise RuntimeError("Failed to create BeautifulSoup object from HTML content")

    # Find and parse the results table
    table = soup.find('table')
    if not table:
        raise ValueError("No HTML table found in the results page. "
                        "The page structure may have changed or the URL may be incorrect.")
    
    print_debug3("Table found, extracting data...")
    
    # Extract all table rows
    rows = table.find_all('tr')
    if len(rows) < 2:
        raise ValueError(f"Table has insufficient rows ({len(rows)}). "
                        f"Expected at least 2 rows (header + data), but found {len(rows)}")
    
    table_data = []
    for i, row in enumerate(rows):
        row_data = []
        cells = row.find_all('td')
        
        # Skip header row (typically has 'th' elements instead of 'td')
        if not cells and i == 0:
            continue
            
        for cell in cells:
            cell_text = cell.get_text().strip()
            row_data.append(cell_text)
        
        if row_data:  # Only add non-empty rows
            table_data.append(row_data)
    
    if len(table_data) < 2:
        raise ValueError(f"Insufficient data rows found ({len(table_data)}). "
                        f"Expected at least 2 rows (data + eliminations)")

    # Extract and process table headers
    headers = table.find_all('th')
    if not headers:
        raise ValueError("No table headers (th elements) found. Cannot determine column structure.")
    
    header_row = [header.get_text().strip() for header in headers]
    if not header_row or not any(header_row):
        raise ValueError("All table headers are empty. Cannot create meaningful DataFrame columns.")
    
    # Add custom headers for mobile compatibility and KC names
    header_row = header_row[:1] + ["Place (mobile)", "KC names"] + header_row[1:]
    print_debug3(f"Table headers: {header_row}")

    # Validate data structure before creating DataFrame
    data_rows = table_data[:-1]  # All rows except the last (eliminations)
    if not data_rows:
        raise ValueError("No data rows found after excluding elimination row")
    
    # Check if all data rows have consistent column count
    expected_columns = len(header_row)
    for i, row in enumerate(data_rows):
        if len(row) != expected_columns:
            print_debug3(f"Warning: Row {i} has {len(row)} columns, expected {expected_columns}")
            # Pad or trim row to match header length
            if len(row) < expected_columns:
                row.extend([''] * (expected_columns - len(row)))
            else:
                row = row[:expected_columns]
            data_rows[i] = row

    try:
        df = pd.DataFrame(data_rows, columns=header_row)
        print_debug3(f"DataFrame created with {len(df)} rows and {len(df.columns)} columns")
    except Exception as e:
        raise RuntimeError(f"Failed to create pandas DataFrame: {e}")

    # Parse elimination data from the last row
    elimination_row = table_data[-1]
    if not elimination_row:
        raise ValueError("Last table row (eliminations) is empty")
    
    if len(elimination_row) == 0:
        print_debug3("No elimination data found in last table row")
        eliminations = []
    else:
        eliminations_raw = elimination_row[0]
        if not eliminations_raw or not eliminations_raw.strip():
            print_debug3("Elimination cell is empty")
            eliminations = []
        else:
            # Clean up the elimination text
            eliminations_text = eliminations_raw.replace("Eliminated", "").strip()
            if eliminations_text.startswith(":"):
                eliminations_text = eliminations_text[1:].strip()
            
            if not eliminations_text:
                eliminations = []
            else:
                # Split by comma and clean each entry
                # eliminations = [entry.strip() for entry in eliminations_text.split(",") if entry.strip()]
                eliminations = process_eliminations(eliminations_text)
            
            print_debug3(f"Parsed {len(eliminations)} eliminations")

    # Final validation
    if df.empty:
        raise ValueError("Resulting DataFrame is empty - no valid competition data found")

    df,status = process_class_df(df)
    assert isinstance(df, pd.DataFrame), "Processed results should be a DataFrame"
    assert isinstance(eliminations, list), "Eliminations should be a list"
    assert isinstance(status, str), "Status should be a string"
    # Output summary information
    print_debug3(f"Results DataFrame for {show_class.class_type}:\n", df.head())
    print_debug3(f"Eliminations array ({len(eliminations)} entries): {eliminations[:3] if len(eliminations) >= 3 else eliminations}")

    return df, eliminations, status

def import_running_orders(show_class, simulation=False):
    """
    Imports and parses running orders from a web page or local file.
    
    Args:
        show_class (ClassInfo): The ClassInfo object containing the running orders URL and class type.
        simulation (bool): If True, reads from local HTML files instead of web scraping.
    
    Returns:
        DataFrame: pandas DataFrame with running orders and withdrawn status.
    """
    # Validate input parameters
    if not show_class:
        raise ValueError("show_class parameter cannot be None")
    
    if not hasattr(show_class, 'running_orders_url'):
        raise ValueError("show_class must have a running_orders_url attribute")
    
    # Handle case where run is None - return None, None gracefully
    if show_class.running_orders_url is None:
        print_debug3(f"No running order URL provided from {show_class.class_type} - returning None. Class status: {show_class.status}")
        return None, None
    
    # Check for empty string URL
    if not show_class.running_orders_url.strip():
        raise ValueError("show_class running_orders_url cannot be empty string")
    
    if not hasattr(show_class, 'class_type') or not show_class.class_type:
        raise ValueError("show_class must have a valid class_type attribute")
    
    soup = None
    
    if not simulation:
        # Fetch results from web
        print_debug3(f"Fetching results from URL: {show_class.running_orders_url}")
        try:
            response = requests.get(show_class.running_orders_url)
            response.raise_for_status()  # Raises requests.HTTPError for bad status codes
            soup = BeautifulSoup(response.content, 'html.parser')
        except requests.RequestException as e:
            raise requests.RequestException(f"Failed to fetch results from {show_class.running_orders_url}: {e}")
    else:
        # Load results from local simulation files
        print_debug3(f"Loading simulation data for class type: {show_class.class_type}")
        
        if show_class.class_type.lower() == "agility":
            raise ValueError("No simulation file available for agility running orders")
        elif show_class.class_type.lower() == "jumping":
            try:
                simulation_soup = read_from_file("NorthDerbySaves/NorthDerbyRunningOrders_LgeJmp.html")
            except FileNotFoundError:
                raise FileNotFoundError("Simulation file 'NorthDerbySaves/NorthDerbyRunningOrders_LgeJmp.html' not found")
        else:
            raise ValueError(f"Unsupported class type for simulation: '{show_class.class_type}'. "
                           f"Supported types are: 'agility', 'jumping'")
        
        soup = simulation_soup

    if not soup:
        raise RuntimeError("Failed to create BeautifulSoup object from HTML content")

    # Find and parse the results table
    table = soup.find('table')
    if not table:
        raise ValueError("No HTML table found in the results page. "
                        "The page structure may have changed or the URL may be incorrect.")
    
    print_debug3("Table found, extracting data...")
    
    # Extract all table rows
    rows = table.find_all('tr')
    if len(rows) < 2:
        raise ValueError(f"Table has insufficient rows ({len(rows)}). "
                        f"Expected at least 2 rows (header + data), but found {len(rows)}")
    
    table_data = []
    for i, row in enumerate(rows):
        row_data = []
        cells = row.find_all('td')
        
        # Skip header row (typically has 'th' elements instead of 'td')
        if not cells and i == 0:
            continue
            
        for cell in cells:
            cell_text = cell.get_text().strip()
            row_data.append(cell_text)
            
        
        if row_data:  # Only add non-empty rows
            table_data.append(row_data)
    
    if len(table_data) < 2:
        raise ValueError(f"Insufficient data rows found ({len(table_data)}). "
                        f"Expected at least 2 rows (data + eliminations)")

    # Extract and process table headers
    headers = table.find_all('th')
    if not headers:
        raise ValueError("No table headers (th elements) found. Cannot determine column structure.")
    
    header_row = [header.get_text().strip() for header in headers]
    header_row = header_row
    print_debug3(f"Table headers: {header_row}")

    try:
        df = pd.DataFrame(table_data, columns=header_row)
        print_debug3(f"DataFrame created with {len(df)} rows and {len(df.columns)} columns")
    except Exception as e:
        raise RuntimeError(f"Failed to create pandas DataFrame: {e}")

    # Check for 'Withdrawn' in 'Name' column. Add a 'Withdrawn' column if found.
    if 'Name' in df.columns:
        df['Withdrawn'] = df['Name'].apply(lambda x: 'Yes' if 'Withdrawn' in x else 'No')
        df['Name'] = df['Name'].str.replace('(Withdrawn)', '').str.strip()
    else:
        print_debug3("No 'Name' column found; cannot determine withdrawals")

    print_debug3(f"Running Orders DataFrame for {show_class.class_type}:\n", df.head())
    return df

if __name__ == "__main__":
    from .KC_ShowProcesser import find_closest_shows, check_show_in_closest, is_close_match
    from .plaza_scraper import find_champ_classes
    from .models import ClassInfo

    print(f"({__name__}) From `plaza_resultsRunningOrder.py` \n({__name__}) Running import_results and import_running_orders tests...")

    print("\n==== Testing Results Importer (simulation save)====")
    # Load simulation data
    simulation_soup = read_from_file(os.path.join("NorthDerbySaves", "NorthDerbyShow_SecondClass.html"))
    agility_class, jumping_class,_ = find_champ_classes(simulation_soup, 'Lge')
    jumping_class_results, jumping_class_eliminations,_ = import_results(jumping_class, simulation=True)
    jumping_running_orders = import_running_orders(jumping_class, simulation=True)

    # Check the types of outputs
    assert isinstance(jumping_class_results, pd.DataFrame), "Results should be a DataFrame"
    assert isinstance(jumping_running_orders, pd.DataFrame), "Running orders should be a DataFrame"
    assert isinstance(agility_class, ClassInfo), "Agility class should be a ClassInfo instance"
    assert isinstance(jumping_class, ClassInfo), "Jumping class should be a ClassInfo instance"
    assert isinstance(jumping_class_eliminations, list), "Eliminations should be a list"

    # Print summaries
    print(f"({__name__})",f"Jumping Results DataFrame ({type(jumping_class_results)}):\n", jumping_class_results.head())
    print(f"\n({__name__})",f"Jumping Running Orders DataFrame ({type(jumping_running_orders)}):\n", jumping_running_orders.head())