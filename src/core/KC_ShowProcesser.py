"""Processing logic for the available shows."""
import pandas as pd
from datetime import datetime
from src.core.debug_logger import print_debug,print_debug3
import difflib

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
    # print_debug(f"Closest Shows from Function:\n", champ_shows_df[["Show Name", "Date", "timedelta", "is_future"]])
    return champ_shows_df

def check_show_in_closest(Target_show_name,closest_shows_df):
    """
    Checks if the target show name exists within the list of closest shows. using `find_closest_shows` function.
    Args:
        Target_show_name (str): The name of the show to search for.
        closest_shows_df (DataFrame): DataFrame of closest shows, usually obtained from `find_closest_shows`.
    Returns:
        tuple (str, datetime): The matched show name and its date from the closest shows list.
        
    Raises:
        ValueError: If the target show name is not found in the closest shows.
    Side Effects:
        Prints a debug message if the target show is found.
    """

    # closest_shows_df = find_closest_shows(*args, **kwargs)
    show_names = closest_shows_df["Show Name"].to_list()
    match = next((name for name in show_names if name.strip().lower() == Target_show_name.strip().lower()), None)
    date = closest_shows_df.loc[closest_shows_df['Show Name'] == match, 'Date'].values[0] if match else None
    print_debug(f"Date of matched show '{match}': {date}")
    if not match:
        raise ValueError(f"Target show '{Target_show_name}' not found in closest shows.")
    else:
        print_debug(f"Target show '{match}' found in closest shows.")
        return match, date

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

def Find_duplicates(df):
    """
    Check for duplicate dog names in the results DataFrame and split the 'Name' column into 'Dog' and 'Handler' columns."""
    #Validate input
    if df is None or df.empty:
        raise ValueError("Input DataFrame is None or empty")
    
    # If there is a Name column, split it into Dog Name and Handler Name
    if 'Name' in df.columns:
        df[['Handler', 'Dog']] = df['Name'].str.split(' & ', expand=True)
        df.drop(columns=['Name'], inplace=True)
    else:
        raise ValueError("No 'Name' column found in DataFrame to split into Dog and Handler")
    #if there is the same name for a dog then print warning
    if df['Dog'].duplicated().any():
        duplicated_dogs = df[df['Dog'].duplicated(keep=False)]['Dog'].unique()
        print_debug3(f"Warning: Duplicate dog names found: {duplicated_dogs}")
    else:
        print_debug3("No duplicate dog names found.")
    return df


if __name__ == "__main__":
    test_show_name = "North Derbyshire Dog Agility Club"

    print("\n==== Testing find shows function can read csv ====")
    closest_shows_df = find_closest_shows(champ_shows_filepath="champ shows.csv", days_ahead=0, num_shows=30)
    print_debug(f"Closest Shows:\n{closest_shows_df[['Show Name', 'Date']].head()}")

    print("\n==== Testing check show in show dataset ====")
    try:
        matched_show,date = check_show_in_closest(test_show_name, closest_shows_df)
        print_debug(f"Matched Show: {matched_show}, Date: {date} ({type(date)})")
    except ValueError as e:
        print_debug(str(e))