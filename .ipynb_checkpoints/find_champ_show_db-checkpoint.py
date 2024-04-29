import requests
from bs4 import BeautifulSoup
import numpy as np
from urllib.parse import urljoin
import pandas as pd
from datetime import datetime

def database():
    heights = ['Lge', 'Int', 'Med', 'Sml']
    champ_show_link = "https://www.thekennelclub.org.uk/events-and-activities/agility/already-competing-in-agility/qualifying-shows-for-the-kennel-club-events/"
    
    response = requests.get(champ_show_link)
    champ_soup = BeautifulSoup(response.content, 'html.parser')
    
    # print(type(champ_show_link))
    
    soup = champ_soup.find_all("details", class_ = "a-details")
    
    for event in soup:
        summaries = event.find_all("summary")
        for summary in summaries:
            if "Championship" in summary.get_text():
                height  = summary.get_text().split(' ')[-1]
                
    
    # Initialize dictionaries to store data
    data = {'small': [], 'medium': [], 'intermediate': [], 'large': []}
    
    # Iterate through events
    for event in soup:
        summaries = event.find_all("summary")
        for summary in summaries:
            # Find the table after the summary
            table = summary.find_next("table")
            if "Championship" in summary.get_text():
    #             print(summary.get_text())
    
                # Find the table after the summary
                table = summary.find_next("table")
                
                #Find the height
                height  = summary.get_text().split(' ')[-1]
                if table:
                    # Extract and process table content
                    for row in table.find_all("tr"):
                        cells = row.find_all("td")
                        if cells:
                            show_name = [cell.get_text(strip=True) for cell in cells][0].lower()
                            # Extract date
                            date = [cell.get_text(strip=True) for cell in cells][1]
                            # Append show name and date to respective height category
                            data[height.lower()].append((show_name, date))
    
                            
    # Combine data for all heights
    combined_data = []
    
    # Create set of all show names
    all_show_names = set()
    for height_shows in data.values():
        for show in height_shows:
            all_show_names.add(show[0])
    
    # Iterate through all show names and check if each height is present
    for show_name in all_show_names:
        show_info = {'Show Name': show_name}
        for height, height_shows in data.items():
            height_present = any(show[0] == show_name for show in height_shows)
            show_info[height.capitalize()] = height_present
        combined_data.append(show_info)
    
    # Create combined dataframe
    combined_df = pd.DataFrame(combined_data)
    
    # Add date column to combined dataframe
    for height, height_shows in data.items():
        for show in height_shows:
            show_name = show[0]
            date = show[1]
            combined_df.loc[combined_df['Show Name'] == show_name, 'Date'] = date
    
    
    # Extracting date and comments
    dates = []
    comments = []
    for item in combined_df['Date']:
        date_parts = item.split('(')
        date = date_parts[0].strip()
        comment = date_parts[1].strip(')') if len(date_parts) > 1 else ''
        dates.append(date)
        comments.append(comment)
    
    # Creating a DataFrame
    # data = {'Date': dates, 'Comments': comments}
    combined_df['Date'] = dates
    combined_df['Comments'] = comments
    # Convert 'Date' column to datetime
    combined_df['Date'] = pd.to_datetime(combined_df['Date'], errors='coerce')

    #Remove "The Agility Club"
    the_agility_club_df = combined_df[combined_df['Show Name'] == 'the agility club']
    the_agility_club_df['Show Name'][0] = 'agility club'
    
    # Now, remove these rows from the original DataFrame
    combined_df = combined_df[combined_df['Show Name'] != 'the agility club']
    
    
    remove_words = ['DTC', 'Dog', 'Training', 'Society', 'and', '&', 'Club', 'in', 'In', 'Obedience', '(Dorset)', 'District', '(Lancs)', 'Show', 'Championship', 'agility']
    remove_words = np.char.lower(remove_words)
    def clean_title(title):
        words = title.split()
        cleaned_words = [word for word in words if word not in remove_words]
        return ' '.join(cleaned_words)
    
    # Apply the cleaning function to the 'Show Name' column
    combined_df['Show Name'] = combined_df['Show Name'].apply(clean_title)
    
    # Group by both 'Show Name' and 'Date' and aggregate with 'any' to combine rows
    combined_df = combined_df.groupby(['Show Name', 'Date']).any().reset_index()

    # Create 'combined_df' by concatenating 'df' and 'the_agility_club'
    combined_df = pd.concat([combined_df, the_agility_club_df])
    
    # Resetting index if needed
    combined_df.reset_index(drop=True, inplace=True)

    #Sort by date
    combined_df = combined_df.sort_values(by='Date')
    
    # combined_df.to_csv('Champ shows lowercase.csv')

    return combined_df



if __name__ == "__main__":
    combined_df = database()
    combined_df.to_csv('Champ shows.csv')
    print(combined_df)