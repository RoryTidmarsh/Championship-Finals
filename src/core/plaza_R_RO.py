"""Module for importing and parsing competition results and running order pages from agilityplaza.com. Returning pandas DataFrames of the main tables."""
import requests
from bs4 import BeautifulSoup
import os
from .debug_logger import *
from .models import ClassInfo
from urllib.parse import urljoin
import pandas as pd
from .plaza_scraper import get_soup
from .constants import PLAZA_RESULTS as base_url
from .error_logger import log_error, log_info

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

def process_class_df(df, request_id=None):
    """Normalise a raw results DataFrame to a standard column set and detect class status.

    The Agility Plaza website uses different header names depending on whether a
    class is still running ("Rank") or has finished ("Place").  Both pages also
    include two hidden mobile/KC columns that are not reflected in the <th> tags
    but ARE present as <td> cells.

    After this function, columns are always:
        ['Rank', 'Place (mobile)', 'KC names', 'Name', 'Run Data', 'Faults', 'Time']

    Args:
        df:         Raw DataFrame built directly from the HTML table.
        request_id: Optional request identifier for error-log correlation.

    Returns:
        (df, status) where status is "completed" or "in progress".
    """
    WANTED = ['Rank', 'Place (mobile)', 'KC names', 'Name', 'Run Data', 'Faults', 'Time']
    headers = df.columns.tolist()

    log_info(
        source="process_class_df",
        message=f"Raw table headers: {headers}",
        request_id=request_id,
        context={"actual_headers": headers, "expected_headers": WANTED},
    )

    # Detect status from the first column name.
    # Completed pages use "Place"; in-progress pages use "Rank".
    first_col = headers[0] if headers else ""
    if first_col == "Place":
        status = "completed"
    elif first_col == "Rank":
        status = "in progress"
    else:
        # Unknown first column – log the anomaly and treat as in-progress so we
        # still attempt to show partial data rather than crashing outright.
        log_error(
            error_type="ColumnMismatch",
            source="process_class_df",
            cause=(
                f"Unexpected first column '{first_col}'. "
                f"Expected 'Rank' (in-progress) or 'Place' (completed). "
                f"Full headers received: {headers}. "
                f"Expected headers: {WANTED}. "
                "Treating class as in-progress; results may be incomplete."
            ),
            request_id=request_id,
            context={"actual_headers": headers, "expected_headers": WANTED},
        )
        status = "in progress"

    # Warn if the number of columns differs from expected
    if len(headers) != len(WANTED):
        log_error(
            error_type="ColumnCountMismatch",
            source="process_class_df",
            cause=(
                f"Table has {len(headers)} columns but {len(WANTED)} were expected. "
                f"Actual columns: {headers}. "
                f"Expected columns: {WANTED}. "
                "This usually means the Agility Plaza page structure has changed. "
                "Column data may be misaligned."
            ),
            request_id=request_id,
            context={"actual_headers": headers, "expected_headers": WANTED, "col_count": len(headers)},
        )

    # Always rename to the standard set so downstream merge logic is consistent.
    # If there is a column-count mismatch we pad / trim to avoid crashing.
    if len(headers) < len(WANTED):
        for col in WANTED[len(headers):]:
            df[col] = None
    df.columns = WANTED[:len(df.columns)]

    # Extract numeric Rank and mobile-Place, stripping any non-digit characters
    # (e.g. "1(T)" for ties on completed pages).
    try:
        df['Rank'] = df['Rank'].astype(str).str.extract(r'(\d+)').astype(int)
    except (ValueError, TypeError) as exc:
        log_error(
            error_type="ColumnParseError",
            source="process_class_df",
            cause=f"Could not parse 'Rank' column to integers: {exc}. Values: {df['Rank'].tolist()[:5]}",
            request_id=request_id,
            exc=exc,
        )
        raise ValueError(
            f"'Rank' column contains non-numeric values that could not be parsed. "
            f"Sample values: {df['Rank'].tolist()[:5]}. Original error: {exc}"
        ) from exc

    try:
        df['Place (mobile)'] = df['Place (mobile)'].astype(str).str.extract(r'(\d+)').astype(int)
    except (ValueError, TypeError) as exc:
        log_error(
            error_type="ColumnParseError",
            source="process_class_df",
            cause=f"Could not parse 'Place (mobile)' column to integers: {exc}. Values: {df['Place (mobile)'].tolist()[:5]}",
            request_id=request_id,
            exc=exc,
        )
        raise ValueError(
            f"'Place (mobile)' column contains non-numeric values that could not be parsed. "
            f"Sample values: {df['Place (mobile)'].tolist()[:5]}. Original error: {exc}"
        ) from exc

    log_info(
        source="process_class_df",
        message=f"Normalised to {len(WANTED)} columns, status='{status}', rows={len(df)}",
        request_id=request_id,
    )
    return df, status


def import_results(show_class, simulation=False, request_id=None):
    """
    Imports and parses competition results from a web page or local file.
    
    Args:
        show_class (ClassInfo): The ClassInfo object containing the results URL and class type.
        simulation (bool): If True, reads from local HTML files instead of web scraping.
        request_id (str|None): Optional ID for error-log correlation.
    
    Returns:
        tuple: (DataFrame, list, str) containing:
            - df: pandas DataFrame with competition results
            - eliminations: list of eliminated competitors
            - status: "completed" or "in progress"
    
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
    
    # Handle case where results_url is None
    if show_class.results_url is None:
        raise ValueError(
            f"No results URL set on the {show_class.class_type} class. "
            f"Current class status: {show_class.status}. "
            "A results URL is required before results can be imported."
        )
    
    # Check for empty string URL
    if not show_class.results_url.strip():
        raise ValueError("show_class results_url cannot be empty string")
    
    if not hasattr(show_class, 'class_type') or not show_class.class_type:
        raise ValueError("show_class must have a valid class_type attribute")
   
    soup = None
    raw_html: str | None = None  # kept for HTML snapshot on error
    
    if not simulation:
        url = show_class.results_url
        print_debug3(f"Fetching results from URL: {url}")
        log_info(
            source="import_results",
            message=f"Fetching {show_class.class_type} results from Agility Plaza",
            request_id=request_id,
            context={"url": url, "class_type": show_class.class_type},
        )
        try:
            response = requests.get(url, timeout=15)
            if response.status_code != 200:
                raw_html = response.text
                log_error(
                    error_type="NetworkError",
                    source="import_results",
                    cause=(
                        f"HTTP {response.status_code} fetching {show_class.class_type} results "
                        f"from {url}. "
                        "The Agility Plaza page may be temporarily unavailable."
                    ),
                    request_id=request_id,
                    context={"url": url, "class_type": show_class.class_type, "http_status": response.status_code},
                    html_snapshot=raw_html,
                )
                raise RuntimeError(
                    f"HTTP {response.status_code} received when fetching {show_class.class_type} results from {url}. "
                    "Agility Plaza may be temporarily unavailable."
                )
            raw_html = response.text
            soup = BeautifulSoup(raw_html, "html.parser")
        except requests.RequestException as e:
            log_error(
                error_type="NetworkError",
                source="import_results",
                cause=f"Network request failed for {show_class.class_type} results at {url}: {e}",
                request_id=request_id,
                context={"url": url, "class_type": show_class.class_type},
                exc=e,
            )
            raise RuntimeError(
                f"Network error fetching {show_class.class_type} results from {url}: {e}"
            ) from e
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
        error_msg = (
            f"No HTML table found in the {show_class.class_type} results page at "
            f"{show_class.results_url}. "
            "The Agility Plaza page structure may have changed, or the URL may point to "
            "a page that doesn't contain results yet."
        )
        log_error(
            error_type="ScrapingError",
            source="import_results",
            cause=error_msg,
            request_id=request_id,
            context={"url": show_class.results_url, "class_type": show_class.class_type},
            html_snapshot=raw_html,
        )
        raise ValueError(error_msg)
    
    print_debug3("Table found, extracting data...")
    
    # Extract all table rows
    rows = table.find_all('tr')
    if len(rows) < 2:
        error_msg = (
            f"The {show_class.class_type} results table at {show_class.results_url} "
            f"contains only {len(rows)} row(s) but at least 2 are required "
            "(1 header row + at least 1 data row). "
            "The class may not have any results yet."
        )
        log_error(
            error_type="ScrapingError",
            source="import_results",
            cause=error_msg,
            request_id=request_id,
            context={"url": show_class.results_url, "class_type": show_class.class_type, "row_count": len(rows)},
            html_snapshot=raw_html,
        )
        raise ValueError(error_msg)
    
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
        error_msg = (
            f"The {show_class.class_type} results table has only {len(table_data)} data row(s). "
            "At least 2 are needed (1 results row + 1 eliminations row). "
            "The class may not have any competitors yet."
        )
        log_error(
            error_type="ScrapingError",
            source="import_results",
            cause=error_msg,
            request_id=request_id,
            context={"url": show_class.results_url, "class_type": show_class.class_type, "row_count": len(table_data)},
            html_snapshot=raw_html,
        )
        raise ValueError(error_msg)

    # Extract and process table headers
    headers = table.find_all('th')
    if not headers:
        error_msg = (
            f"No <th> header elements found in the {show_class.class_type} results table at "
            f"{show_class.results_url}. "
            "The Agility Plaza page structure may have changed."
        )
        log_error(
            error_type="ScrapingError",
            source="import_results",
            cause=error_msg,
            request_id=request_id,
            context={"url": show_class.results_url, "class_type": show_class.class_type},
            html_snapshot=raw_html,
        )
        raise ValueError(error_msg)
    
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
        log_error(
            error_type="ScrapingError",
            source="import_results",
            cause=f"Failed to build DataFrame for {show_class.class_type} results: {e}. Headers: {header_row}",
            request_id=request_id,
            context={"url": show_class.results_url, "class_type": show_class.class_type, "headers": header_row},
            html_snapshot=raw_html,
            exc=e,
        )
        raise RuntimeError(
            f"Could not build a DataFrame from the {show_class.class_type} results table. "
            f"Headers found: {header_row}. Original error: {e}"
        ) from e

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
                eliminations = process_eliminations(eliminations_text)
            
            print_debug3(f"Parsed {len(eliminations)} eliminations")

    # Final validation
    if df.empty:
        raise ValueError("Resulting DataFrame is empty - no valid competition data found")

    df, status = process_class_df(df, request_id=request_id)
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