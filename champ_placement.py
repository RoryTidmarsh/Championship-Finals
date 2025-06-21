import requests
from bs4 import BeautifulSoup
import numpy as np
from urllib.parse import urljoin
import pandas as pd
from datetime import datetime
import re

class plaza:
    def __init__(self, height, JUMPING_url = None, AGILITY_url = None):
        self.base_link = "https://www.agilityplaza.com/results/"
        self.current_date = datetime.now().date()
        self.year = self.current_date.strftime("%Y")
        
        self.current_year_link = self.base_link + str(self.year)
        self.removed_words = np.char.lower(['DTC', 'Dog', 'Training', 'Society', 'and', '&', 'Club', 'in', 'In', 'Obedience', '(Dorset)', 'District', '(Lancs)', 'Show', 'Championship', 'agility'])

        self.jump_url = JUMPING_url
        self.agility_url = AGILITY_url
        self.height = height
        self.round_1_winner = None
        self.round_2_winner = None

        if (self.jump_url ==None)&(self.agility_url==None):
            self.shows_df = pd.read_csv("Champ shows.csv", index_col=0)
            self.shows_df['Date'] = pd.to_datetime(self.shows_df['Date'])
            self.last_show = self.nearest_show(print_statement = False)
            self.next_show = self.nearest_shows(next_show=True)
            self.last_show_results_link = str(self.base_link[:-9]) + (self.recent_show_link())

        
    def month_soup(self, months_ago=0, return_month=False):
        """
        Extracts a portion of HTML soup corresponding to a specific month's data from agility plaza.
    
        Args:
            self: Instance of the class containing the method.
            months_ago (int, optional): An integer indicating how many months ago the function should extract data for. Default is 0, representing the current month.
            return_month (bool, optional): A boolean indicating whether to return the month name along with the soup. Default is False.
    
        Returns:
            list or tuple: If return_month is False, returns a list of HTML elements between the selected month's data. If return_month is True, returns a tuple containing a list of HTML elements and the name of the month.
    
        Description:
            This function sends an HTTP GET request to the URL specified by self.current_year_link, parses the response content using BeautifulSoup, and locates all <thead> elements within the HTML soup. It selects the <thead> element corresponding to the month specified by months_ago (default is 0 for the current month). It retrieves all HTML elements between the selected <thead> element and the next <thead> element. If return_month is set to True, the function extracts the month name from the selected <thead> element. Finally, it returns either the extracted HTML elements or both the HTML elements and the month name, depending on the value of return_month.
        """
        # Send an HTTP GET request to the URL
        url = self.current_year_link
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find all <thead> elements
        theads = soup.find_all("thead")
        
        # Get the first <thead>
        first_thead = theads[months_ago]
    
        # Find the elements between the first and second <thead>
        elements_between = []
        current_element = first_thead.find_next_sibling()
        while current_element and current_element.name != 'thead':
            elements_between.append(current_element)
            current_element = current_element.find_next_sibling()
    
        if return_month:
            month = first_thead.text.strip().split(" ")[0]
            return elements_between, month
        else:
            return elements_between
           
    def recent_champ(self, months_ago=0, print_statement=True):
        """
        Finds the most recent championship competition within a specified range of months.
    
        Args:
            self: Instance of the class containing the method.
            months_ago (int, optional): Number of months ago to start searching for championships. Default is 0, representing the current month.
            print_statement (bool, optional): Whether to print search progress and results. Default is True.
    
        Returns:
            tuple or None: A tuple containing the link and name of the most recent championship competition if found, or None if no championship is found within the specified range.
    
        Description:
            This function searches for the most recent championship competition within a specified range of months. It starts the search from the current month (or a specified number of months ago) and goes back up to 12 months. For each month, it retrieves the HTML soup corresponding to the competition data and checks if any competition contains the word "Championship" in its name. If a championship is found, it returns a tuple containing the link and name of the championship competition. If no championship is found within the specified range, it returns None. The function optionally prints search progress and results based on the value of the print_statement parameter.
        """
        max_months = 12  # Maximum number of months to go back
        for i in range(months_ago, max_months + 1):
            month_soup = self.month_soup(i)
            Name = None
            link = None
    
            for j in range(1, len(month_soup)):
                td_element = month_soup[j].find_all('td')[-1]
    
                if "Championship" in td_element.text:
                    Name = td_element.text
                    link =  self.base_link[:-9] + month_soup[j].get('data-href')
                    if print_statement ==True:
                        print(f"Championship found in {td_element.text}, link {link}")
                        
                    return link, Name  # Exit the function once Championship is found
                    break
    
            if Name is None:
                if print_statement==True:
                    print(f"No competition with 'Championship' in the name was found for {i} months ago. Trying next month.")
                
        if print_statement ==True:
            print("No competition with 'Championship' in the name was found in the last", max_months, "months.")
        return None 

    def find_classes(self, months_ago=0, KC_website = True, print_statement=False):
        """
        Extracts information about championship classes from the agility plaza website and organizes it into a pandas DataFrame.
    
        Args:
            self: Instance of the class containing the method.
            months_ago (int, optional): An integer indicating how many months ago the function should search for championship classes. Default is 0, representing the current month.
            KC_website (bool, optional): A boolean indicating if the most recent championship show should be found by the KC website (True) or by if the show has championship in the name (False), default ==True.
            print_statement (bool, optional): A boolean indicating whether to print statements during the execution of the function. Default is False.
    
        Returns:
            pandas.DataFrame: A DataFrame containing information about championship classes, including the class name, link, and height.
    
        Description:
            This function first retrieves the link and name of the most recent championship competition by calling the 'recent_champ' method. It then sends an HTTP GET request to the retrieved link, parses the response content using BeautifulSoup, and locates all 'card-block' elements within the HTML soup. It iterates through each 'card-block' element to find the championship classes. For each class found, it extracts the class name and link and appends them to a list. After gathering all class information, it creates a pandas DataFrame with columns for the class name, link, and height. The height is derived from the second word in the class name. The function sets the DataFrame index to be composed of the first two words extracted from the class name. Finally, it returns the DataFrame containing the championship class information.
        """
        if KC_website ==True:
            show_link = self.last_show_results_link
        else:
            show_link, show_name = self.recent_champ(months_ago, print_statement)
        
        response = requests.get(show_link)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Finding the day and classes in that day
        div_elements = soup.find_all("div", class_="card-block")
        
        class_data = []
        for day_div in div_elements:
            for a in day_div.find_all('a'):
                if "Championship Jumping" in a.text:
                    name = a.text
                    link = "agilityplaza.com" + a.get('href')
                    class_data.append((name, link))
                    # self.jump_url = link
                elif "Championship Agility" in a.text:
                    name = a.text
                    link = "agilityplaza.com" + a.get('href')
                    class_data.append((name, link))
                    # self.agility_url = link
        
        # Create a pandas DataFrame
        df = pd.DataFrame(class_data, columns=['Class Name', 'Link'])
        df['class number'] = df['Class Name'].apply(lambda x: ' '.join(x.split()[:1]))
        df.set_index('class number', inplace=True)
        df['Height'] = df['Class Name'].apply(lambda x: x.split()[1] if len(x.split()) >= 2 else None)
        df["Type"] = df['Class Name'].apply(lambda x: x.split()[-1] if len(x.split()) >= 2 else None)
        return df

    def nearest_show(self, print_statement=True):
        """
        Finds the nearest show based on the current date.
        
        Returns:
            str: The name of the most recent show if not cancelled. 
        Raises:
            ValueError: If no shows are found in the dataframe or no champ shows have occurred this year yet.
        """
        current_date = pd.Timestamp(datetime.now().date())
        
        past_shows = self.shows_df[self.shows_df['Date'] <= current_date]
        
        if past_shows.empty:
            raise ValueError("No shows found in the dataframe. No champ shows have occurred this year yet")
        
        sorted_df = past_shows.sort_values(by='Date', ascending=False)
        
        most_recent = sorted_df.iloc[0]

        if most_recent['Comments'] == True:
            if print_statement == True:
                print(f"Most recent show ({most_recent['Date']}) was '{most_recent['Show Name']}' but it was cancelled.")
            # Find the previous show before the cancelled one
            prev_show_index = sorted_df.index[sorted_df['Comments'].shift(-1).fillna(False)].tolist()[0]
            prev_show = self.shows_df.loc[prev_show_index]['Show Name']
            return prev_show
        else:
            return most_recent['Show Name']

    def nearest_shows(self, next_show=False, print_statement = True):
        """
        Finds the nearest show based on the current date and the previous show before the cancellation.
        
        Args:
            next_show (bool): If True, returns the next upcoming show instead of the most recent one.
        
        Returns:
            tuple or str: A tuple containing the name of the most recent show and the previous show before cancellation.
                          If next_show is True, returns the name of the next upcoming show.
        Raises:
            ValueError: If no shows are found in the dataframe or no champ shows have occurred this year yet.
        """
        current_date = pd.Timestamp(datetime.now().date())
        
        if next_show==True:
            upcoming_shows = self.shows_df[self.shows_df['Date'] > current_date]
            if upcoming_shows.empty:
                raise ValueError("No upcoming shows found.")
            next_show = upcoming_shows.iloc[0]
            return next_show['Show Name']
            
        else:
            past_shows = self.shows_df[self.shows_df['Date'] <= current_date]
            
            if past_shows.empty:
                raise ValueError("No shows found in the dataframe. No champ shows have occurred this year yet")
            
            sorted_df = past_shows.sort_values(by='Date', ascending=False)
            
            most_recent = sorted_df.iloc[0]
    
            if most_recent['Comments'] == True:
                if print_statement == True:
                    print(f"Most recent show ({most_recent['Date']}) was '{most_recent['Show Name']}' but it was cancelled.")
                # Find the previous show before the cancelled one
                prev_show_index = sorted_df.index[sorted_df['Comments'].shift(-1).fillna(False)].tolist()[0]
                prev_show = self.shows_df.loc[prev_show_index]['Show Name']
                if print_statement ==True:
                    print(f"Previous show before cancellation was '{prev_show}'")
                return most_recent['Show Name'], prev_show
            else:
                return most_recent['Show Name']

    def recent_show_link(self, print_statement=True):
        """
        Retrieves the link associated with the most recent show from the `champ_placement` object. The most recent show is taken from the KC website so if nothing is found then the show might not be on plaza or in this current month.
        
        Args:
            print_statement (bool, optional): If True, prints statements during execution. Defaults to True.
        
        Returns:
            data_href (str): The next part of the link to access the show results page. This needs to be combined to the base link.
        """
        elements = self.month_soup(months_ago = 0)
    
        # Convert each Tag object to a string
        elements_as_strings = [str(element) for element in elements]
        
        # Join the strings
        combined_html = ''.join(elements_as_strings)
        
        # Create a new BeautifulSoup object from the combined HTML
        soup = BeautifulSoup(combined_html, 'html.parser')
    
        
        last_show = self.nearest_show()
        if print_statement ==True:
            print(f"Last show to run was {last_show}")
        
        def clean_title(title):
                words = title.split()
                cleaned_words = [word for word in words if word not in remove_words]
                return ' '.join(cleaned_words)
        
        
        if last_show != "agility club":
            remove_words = self.removed_words
        
        # Find <td> elements containing the last show name
        show_row = soup.find('td', string=lambda text: last_show in clean_title(text.lower()))
        
        #  If the row is found then print
        if show_row:
            if print_statement ==True:
                print("Matching rows found:")
                print(show_row.text)
            
            # Find the parent <tr> tag
            parent_tr = show_row.find_parent('tr')
        
            # Find the data-href attribute within the <tr> tag
            data_href = parent_tr.get('data-href')
        
            # If data-href exists, print it
            if data_href:
                return data_href
                if print_statement ==True:
                    print("Data-href link:", data_href)
            else:
                print("No data-href link found.")
        else:
            print(f'No shows matching "{last_show}" were found this month')
            print("Trying last month...")
            elements = self.month_soup(months_ago = 1)
        
            # Convert each Tag object to a string
            elements_as_strings = [str(element) for element in elements]
            
            # Join the strings
            combined_html = ''.join(elements_as_strings)
            
            # Create a new BeautifulSoup object from the combined HTML
            soup = BeautifulSoup(combined_html, 'html.parser')            
            
            # Find <td> elements containing the last show name
            show_row = soup.find('td', string=lambda text: last_show in clean_title(text.lower()))
            
            #  If the row is found then print
            if show_row:
                if print_statement ==True:
                    print("Matching show found: ", show_row.text )
                
                # Find the parent <tr> tag
                parent_tr = show_row.find_parent('tr')
            
                # Find the data-href attribute within the <tr> tag
                data_href = parent_tr.get('data-href')
            
                # If data-href exists, print it
                if data_href:
                    return data_href
                    if print_statement ==True:
                        print("Data-href link:", data_href)
                else:
                    print("No data-href link found.")
            else:
                raise ValueError(f'No show named "{self.nearest_show(print_statement=False)}" found this month or last month. This may be due to {last_show} not being on Agility Plaza. (or the code is broken @rory)')

    def df_results(self):
        if (self.jump_url ==None)&(self.agility_url==None):
            df = self.find_classes()
            df = df.drop_duplicates(subset="Class Name", keep="first")
            links = np.array(df[df['Height'] == self.height]['Link'])
            links = "https://www." + links
        else:
            links = np.array([self.jump_url, self.agility_url])
        if len(links) ==2:
                   
            #creating an empty list for the data frame of each result to go into
            results_df_list = list(np.zeros(len(links)))
            
            #looping over the list to get the results for both rounds
            for i, link in enumerate(links):
                
                #getting the result soup from the links of each round
                response = requests.get(link)
                soup_results = BeautifulSoup(response.text, 'html.parser')
        
                table_data = []
                table = soup_results.find('table')  # Locate the table
                
                #creating the table that can be used with pandas 
                if table:
                    rows = table.find_all('tr')  # Find all rows in the table
                    for row in rows:
                        row_data = []  # Create a list for each row
                        cells = row.find_all('td')  # Find all cells in the row
                        for cell in cells:
                            row_data.append(cell.get_text())  # Append cell data to the row list
                        table_data.append(row_data)  # Append the row list to the table_data list
        
                # Extract table headings into a list
                column_headings = ['place1', 'place2', 'posh names', 'name', 'type','faults', 'time']
                #dropping the useless columns to us
                df = pd.DataFrame(table_data, columns = column_headings).drop(0).drop(columns=['place1','place2','posh names'])
                #creating a seperate human and dog column
                df[['Human', 'Dog']] = df['name'].str.split(' & ', expand=True)
        
                selected_columns = ['Human', 'Dog']
                
                #creating a new df that only has human and dog columns
                df_new = df[selected_columns]
                results_df_list[i] = df_new
                
            return results_df_list
        elif len(links) ==1:
            print("Only 1 class has run or is running, wait for the other class to start before trying again")
        
        else:
            raise ValueError(f"Height '{self.height}' not found at '{self.nearest_show()}' show")
        
    def overall_results(self):
        '''creates the final overall top 20 and the overall placings
        INPUTS
        organisation_name_to_find - REQUIRED, the name of the organisation/show as shown on Agility Plaza
        first_round_class_name, second_round_class_name - REQUIRED, the name of both of the championship rounds as shown on Agility Plaza, in the order in which they are ran at the competiiton
        
        OUTPUTS
        df_top_20 - pandas dataframe containing the top 20 placings
        df_placings - pandas dataframe containing the overall results, not limited to the top 20'''
        
        #creating the list of the results from both rounds
        results_df_list = self.df_results()
        
        #seperating the 2 result dataframes from the list
        df1 = results_df_list[0] #Round 1
        df2 = results_df_list[1] #Round 2

        self.round_1_winner = df1.iloc[0]
        self.round_2_winner = df2.iloc[0]
            
        # Find common dog-human pairings
        common_pairings = set(zip(df1['Human'], df1['Dog'])) & set(zip(df2['Human'], df2['Dog']))
    
        # Calculate points for each common pairing
        points = {}
        round_1_points = {}
        round_2_points = {}
        for human, dog in common_pairings:
            index1 = df1[(df1['Human'] == human) & (df1['Dog'] == dog)].index
            index2 = df2[(df2['Human'] == human) & (df2['Dog'] == dog)].index
            if not index1.empty and not index2.empty:
                points[(human, dog)] = index1[0] + index2[0]
                round_1_points[(human, dog)] = index1[0]
                round_2_points[(human, dog)] = index2[0]
    
        # Create a new dataframe with pairings and points
        df_points = pd.DataFrame({'Pairing': list(points.keys()), 'Points': list(points.values()), 'Round 1': list(round_1_points.values()), 'Round 2':  list(round_2_points.values())})
    
        # Sort the dataframe by points in ascending order
        df_points = df_points.sort_values(by='Points')
    
        #taking the top 20
        df_top_20 = df_points.head(20)
    
        if len(df_top_20) < 20:
            print(f'Partially filled final, {20 - len(df_top_20)} spots left')
        elif len(df_top_20) == 20:
            print('Full final')
        print("Pairings with Points (Lowest to Highest):")
        df_points['place'] = np.arange(1,len(df_points)+1)
        df_top_20['place'] = np.arange(1,len(df_top_20)+1)
    
        df_points = df_points.set_index('place')
        df_top_20 = df_top_20.set_index('place')
        return df_top_20, df_points

        
if __name__ == "__main__":
    # Example usage
    plaza_instance = plaza(height="Sml", JUMPING_url="https://www.agilityplaza.com/agilityClass/1945889857/results", AGILITY_url= "https://www.agilityplaza.com/agilityClass/1239111043/results")  # Example height
    top_20, all_results = plaza_instance.overall_results()
    
    print("Top 20 Results:")
    print(top_20)
    
    print("\nAll Results:")
    print(all_results)