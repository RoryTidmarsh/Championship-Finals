import requests
from bs4 import BeautifulSoup
import numpy as np
from urllib.parse import urljoin
import pandas as pd
from datetime import datetime

class champ_placement:
    def __init__(self):
        self.base_link = "https://www.agilityplaza.com/results/"
        self.current_date = datetime.now().date()
        self.year = self.current_date.strftime("%Y")
        
        self.current_year_link = self.base_link + str(self.year)
        
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

    def find_classes(self, months_ago=0, print_statement=False):
        """
        Extracts information about championship classes from the agility plaza website and organises it into a pandas DataFrame.
    
        Args:
            self: Instance of the class containing the method.
            months_ago (int, optional): An integer indicating how many months ago the function should search for championship classes. Default is 0, representing the current month.
            print_statement (bool, optional): A boolean indicating whether to print statements during the execution of the function. Default is False.
    
        Returns:
            pandas.DataFrame: A DataFrame containing information about championship classes, including the class name, link, and height.
    
        Description:
            This function first retrieves the link and name of the most recent championship competition by calling the 'recent_champ' method. It then sends an HTTP GET request to the retrieved link, parses the response content using BeautifulSoup, and locates all 'card-block' elements within the HTML soup. It iterates through each 'card-block' element to find the championship classes. For each class found, it extracts the class name and link and appends them to a list. After gathering all class information, it creates a pandas DataFrame with columns for the class name, link, and height. The height is derived from the second word in the class name. The function sets the DataFrame index to be composed of the first two words extracted from the class name. Finally, it returns the DataFrame containing the championship class information.
        """
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
                elif "Championship Agility" in a.text:
                    name = a.text
                    link = "agilityplaza.com" + a.get('href')
                    class_data.append((name, link))
        
        # Create a pandas DataFrame
        df = pd.DataFrame(class_data, columns=['Class Name', 'Link'])
        df['class number'] = df['Class Name'].apply(lambda x: ' '.join(x.split()[:1]))
        df.set_index('class number', inplace=True)
        df['Height'] = df['Class Name'].apply(lambda x: x.split()[1] if len(x.split()) >= 2 else None)
        return df
    

#ch = champ_placement()
#ch.recent_champ(months_ago=2)