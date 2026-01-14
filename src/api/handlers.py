from src.core import *
import src.api.models as API_models
import pandas as pd
import asyncio


async def get_nearby_shows(days_ahead=5, num_shows=5):
    """Fetch shows around the current date."""
    shows_df = KC_ShowProcesser.find_closest_shows(days_ahead=days_ahead, num_shows=num_shows)
    assert isinstance(shows_df, pd.DataFrame), "Expected shows to be a DataFrame"

    # Format DataFrame into relevant cols only
    shows_df = shows_df[['Show Name', 'Date']].rename(columns={'Show Name': 'show', 'Date': 'date'})
    shows_df['date'] = shows_df['date'].dt.strftime('%Y-%m-%d')
    shows_data = shows_df.to_dict(orient='records')
    return API_models.getNearShowsResponse(shows=shows_data)

async def initialise_classInfo(show: str, date: str, height: str):
    """Initialise ClassInfor objects for a given show, date, and height. This is to be called when the webapp moves from '/' to 'finals' route."""
    try:
        # Check if show is in closest shows
        closest_shows_df = KC_ShowProcesser.find_closest_shows()
        matched_show, matched_date = KC_ShowProcesser.check_show_in_closest(show, closest_shows_df)

        # Get show URL
        show_url = plaza_scraper.find_show_url(matched_show, matched_date)
        assert show_url, f"Show URL not found for {matched_show} on {matched_date}"
        assert isinstance(show_url, str), "Expected show_url to be a string"
        
        # Get URLS of the show page
        show_soup = plaza_scraper.get_soup(show_url) # Soup first
        agility_class, jumping_class = plaza_scraper.find_champ_classes(show_soup, height)

    except ValueError as ve:
        raise valueError(ve)

    return agility_class, jumping_class

async def update_classInfo(agility_class: ClassInfo, jumping_class: ClassInfo):
    """Update ClassInfo object of the qualifying rounds. To be called when finals route is refreshed.
    
    
    Returns:
        Tuple of updated ClassInfo objects (agility_class, jumping_class)
    """

    # Import results for agility class
    agility_results_df, agility_eliminations, agility_status = plaza_R_RO.import_results(agility_class)

    # Import results for jumping class
    jumping_results_df, jumping_eliminations, jumping_status = plaza_R_RO.import_results(jumping_class)

    # Update ClassInfo objects
    agility_class.results_df = agility_results_df
    agility_class.eliminations = agility_eliminations
    agility_class.status = agility_status

    jumping_class.results_df = jumping_results_df
    jumping_class.eliminations = jumping_eliminations
    jumping_class.status = jumping_status

    agility_class.update_order(jumping_class)

    assert isinstance(agility_class, ClassInfo), "Expected agility_class to be ClassInfo"
    assert isinstance(jumping_class, ClassInfo), "Expected jumping_class to be ClassInfo"
    assert agility_class.order != jumping_class.order, "Classes should have different orders"

    return agility_class, jumping_class
    

if __name__ == "__main__":
    
    print("Running API handlers module tests...")
    
    print(asyncio.run(get_nearby_shows()))

    print("\n==== Testing get_class_ids function ====")
    test_show = "North Derbyshire Dog Agility Club"
    test_date = "2025-09-14"
    test_height = "Large"
    show,date = asyncio.run(get_class_ids(test_show, test_date, test_height))
    print(f"Agility ID: {show}, Jumping ID: {date}")

