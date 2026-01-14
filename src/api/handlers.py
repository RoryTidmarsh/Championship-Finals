from src.core import *
import src.api.models as API_models
import pandas as pd


async def get_nearby_shows(days_ahead=5, num_shows=5):
    """Fetch shows around the current date."""
    shows_df = KC_ShowProcesser.find_closest_shows(days_ahead=days_ahead, num_shows=num_shows)
    assert isinstance(shows_df, pd.DataFrame), "Expected shows to be a DataFrame"

    # Format DataFrame into relevant cols only
    shows_df = shows_df[['Show Name', 'Date']].rename(columns={'Show Name': 'show', 'Date': 'date'})
    shows_df['date'] = shows_df['date'].dt.strftime('%Y-%m-%d')
    shows_data = shows_df.to_dict(orient='records')
    return API_models.getNearShowsResponse(shows=shows_data)

async def get_class_ids(show: str, date: str, height: str):
    """Fetch class IDs based on show, date, and height."""
    agilityID, jumpingID = await get_class_ids_core(show, date, height)
    return agilityID, jumpingID


if __name__ == "__main__":
    print("Running API handlers module tests...")
    
    print(get_nearby_shows())
