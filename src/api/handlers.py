from src.core import *
import src.api.models as API_models
import pandas as pd
import os
import asyncio
from src.core.models import ClassInfo, Final
from src.api.session import session

async def get_nearby_shows(days_ahead=5, num_shows=5):
    """Fetch shows around the current date."""
    try:
        shows_df = KC_ShowProcesser.find_closest_shows(days_ahead=days_ahead, num_shows=num_shows)
        assert isinstance(shows_df, pd.DataFrame), "Expected shows to be a DataFrame"
    except Exception as e:
        raise ValueError(f"Error fetching nearby shows: {e}")

    # Format DataFrame into relevant cols only
    shows_df = shows_df[['Show Name', 'Date']].rename(columns={'Show Name': 'show', 'Date': 'date'})
    shows_df['date'] = shows_df['date'].dt.strftime('%Y-%m-%d')
    shows_data = shows_df.to_dict(orient='records')
    return API_models.getNearShowsResponse(shows=shows_data)

async def initialise_classInfo(show: str, height: str):
    """Initialise ClassInfor objects for a given show height. This is to be called when the webapp moves from '/' to 'finals' route."""
    try:
        # Check if show is in closest shows
        closest_shows_df = KC_ShowProcesser.find_closest_shows()
        matched_show, matched_date = KC_ShowProcesser.check_show_in_closest(show, closest_shows_df)
        print_debug(f"Matched show: {matched_show} on {matched_date}")
    except Exception as e:
        raise ValueError(f"Error finding show '{show}': {e}")
    try:
        # Get show URL
        show_url = plaza_scraper.find_show_url(matched_show, matched_date)
        assert show_url, f"Show URL not found for {matched_show} on {matched_date}"
        assert isinstance(show_url, str), "Expected show_url to be a string"
        print_debug(f"Found show URL: {show_url}")
    except Exception as e:
        raise ValueError(f"Error getting show URL: {e}")

    try:
        # Get URLS of the show page
        show_soup = plaza_scraper.get_soup(show_url) # Soup first

        assert show_soup, "Failed to retrieve show page soup"
        print_debug(f"Retrieved show page soup for URL: {show_url}")
    except Exception as e:
        raise ValueError(f"Error fetching show page soup: {e}")
    try:
        agility_class, jumping_class = plaza_scraper.find_champ_classes(show_soup, height)

        assert isinstance(agility_class, ClassInfo), "Expected agility_class to be ClassInfo"
        assert isinstance(jumping_class, ClassInfo), "Expected jumping_class to be ClassInfo"

        agilityID = plaza_scraper.extract_class_id(agility_class.results_url)
        jumpingID = plaza_scraper.extract_class_id(jumping_class.results_url)
        
        print_debug(f"agilityID: {agilityID}, jumpingID: {jumpingID}")
    except Exception as e:
        raise ValueError(f"Error initializing ClassInfo objects: {e}")

    return API_models.getClassIDsResponse(agilityID=agilityID, jumpingID=jumpingID)

async def get_class_ids(agility_link: str, jumping_link: str):
    """Extract class IDs from the provided class links."""
    try:
        agility_id = plaza_scraper.extract_class_id(agility_link)
        jumping_id = plaza_scraper.extract_class_id(jumping_link)

        assert isinstance(agility_id, str), "Expected agility_id to be a string"
        assert isinstance(jumping_id, str), "Expected jumping_id to be a string"

    except Exception as e:
        raise ValueError(f"Error extracting class IDs: {e}")

    return API_models.lookupIDsResponse(agilityID=agility_id, jumpingID=jumping_id)

async def update_classInfo(agilityID: str, jumpingID: str, simulation=False):
    """Update ClassInfo object of the qualifying rounds. To be called when finals route is refreshed.
    
    
    Returns:
        Tuple of updated ClassInfo objects (agility_class, jumping_class)
    """
    # Construct URLs from IDs (use forward slashes for URLs, not os.path.join)
    agilityURL = f"{PLAZA_BASE}/agilityClass/{agilityID}/results"
    jumpingURL = f"{PLAZA_BASE}/agilityClass/{jumpingID}/results"

    print_debug(f"Agility Results URL: {agilityURL}")
    print_debug(f"Jumping Results URL: {jumpingURL}")
    # agility_RunningOrderURL = os.path.join(PLAZA_BASE, "/agilityClass", agilityID,"running_orders")
    # jumping_RunningOrderURL = os.path.join(PLAZA_BASE, "agilityClass", jumpingID,"running_orders")


    agility_class = ClassInfo("Agility",results_url=agilityURL)
    jumping_class = ClassInfo("Jumping",results_url=jumpingURL)
    agility_class.classID = agilityID
    jumping_class.classID = jumpingID
    
    if not agility_class or not jumping_class:
        raise ValueError("ClassInfo objects not initialized in session. Please initialise first.")

    try:
        # Import results for agility class
        agility_results_df, agility_eliminations, agility_status = plaza_R_RO.import_results(agility_class, simulation=simulation)

        # Import results for jumping class
        jumping_results_df, jumping_eliminations, jumping_status = plaza_R_RO.import_results(jumping_class, simulation=simulation)
    except Exception as e:
        raise ValueError(f"Error importing results: {e}")

    # Update ClassInfo objects
    agility_class.results_df = agility_results_df
    agility_class.eliminations = agility_eliminations
    agility_class.status = agility_status

    jumping_class.results_df = jumping_results_df
    jumping_class.eliminations = jumping_eliminations
    jumping_class.status = jumping_status

    # Update the class order
    agility_class.update_order(jumping_class)

    # Check expected types
    assert isinstance(agility_class, ClassInfo), "Expected agility_class to be ClassInfo"
    assert isinstance(jumping_class, ClassInfo), "Expected jumping_class to be ClassInfo"

    if jumping_class.status == "in progress":
        jumping_class.running_orders_url = jumping_RunningOrderURL
    if agility_class.status == "in progress":
        agility_class.running_orders_url = agility_RunningOrderURL

    final_class = Final(jumping_class, agility_class)
    final_class.combine_dfs()
    final_class.update_status()
    return API_models.update_classesResponse(agilityClass=agility_class, jumpingClass=jumping_class, finalClass=final_class)
    

if __name__ == "__main__":
    
    agility_id, jumping_id = asyncio.run(initialise_classInfo("lisburn", "lge"))
    
    print_debug(f"Agility ID: {agility_id}, Jumping ID: {jumping_id}")

    agility_class, jumping_class = asyncio.run(update_classInfo(agility_id, jumping_id, simulation=False))

    print_debug(agility_class)
    print_debug(jumping_class)


