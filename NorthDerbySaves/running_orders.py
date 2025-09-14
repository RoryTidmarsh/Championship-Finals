import requests
from bs4 import BeautifulSoup
import numpy as np
from urllib.parse import urljoin
import pandas as pd
from datetime import datetime
import re
import os

"""
Files to create:
- NorthDerbyShow_SecondClass.html: HTML file of the results page of ND show while the second round of champ is running.
- NorthDerbyShow_LgeJmp_incomplete.html: HTML file of the results page of ND show while the large jump is running.

Files we have:
- Running orders of 2nd champ round, Lge jmp
- HTML of results page while only large agility is shown. This has results link to the first class and links to both running orders.
- HTML of large champ agility when the class is completed. 
"""
dir_path = os.path.dirname(os.path.realpath(__file__))
NorthDerbyURL_1stClass = "https://www.agilityplaza.co.uk/competition/1205629450/results"
ND_LgeAgURL = "https://www.agilityplaza.co.uk/agilityClass/1263911657/results"
ND_LgeJmpURL = "https://www.agilityplaza.co.uk/agilityClass/1799909160/results"
NorthDerbyURL_2ndClass = "https://www.agilityplaza.co.uk/competition/1205629450/results"

def write_to_file(soup, filename="NorthDerbyShow.txt"):
    base, ext = os.path.splitext(filename)
    counter = 1
    new_filename = filename
    while os.path.exists(new_filename):
        new_filename = f"{base}_{counter}{ext}"
        counter += 1
    with open(new_filename, "w", encoding="utf-8") as f:
        f.write(soup.prettify())
    print(f"Saved to {new_filename}")

response = requests.get(NorthDerbyURL_2ndClass)
soup = BeautifulSoup(response.content, 'html.parser')
# Write the file once, then comment this out and use read_from_file()
write_to_file(soup, dir_path + "\\NorthDerbyShow_SecondClass.html")





def read_from_file(filename="NorthDerbyShow.txt"):
    with open(filename, "r", encoding="utf-8") as f:      
        html = f.read()
    soup = BeautifulSoup(html, 'html.parser')
    return soup


# RunningOrdersURL = "https://www.agilityplaza.co.uk/agilityClass/1799909160/running_orders"
# response = requests.get(RunningOrdersURL)
# RunningOrderSoup = BeautifulSoup(response.content, 'html.parser')
# write_to_file(RunningOrderSoup, "NorthDerbyRunningOrders_LgeJmp.txt")

RO_soup = read_from_file(dir_path + "\\NorthDerbyRunningORders_LgeJmp.html")
print(RO_soup.prettify()[:1000])  # Print the first 1000 characters to verify content
