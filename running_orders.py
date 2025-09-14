import requests
from bs4 import BeautifulSoup
import numpy as np
from urllib.parse import urljoin
import pandas as pd
from datetime import datetime
import re
import os

NorthDerbyURL = "https://www.agilityplaza.co.uk/competition/1205629450/results"

response = requests.get(NorthDerbyURL)
soup = BeautifulSoup(response.content, 'html.parser')

def write_to_file(soup, filename="NorthDerbyShow.txt"):
    with open(filename, "w", encoding="utf-8") as f:
        f.write(soup.prettify())

## Write the file once, then comment this out and use read_from_file()
# write_to_file(soup)

def read_from_file():
    with open("NorthDerbyShow.txt", "r", encoding="utf-8") as f:
        html = f.read()
    soup = BeautifulSoup(html, 'html.parser')
    return soup

print(soup.prettify())

RunningOrdersURL = "https://www.agilityplaza.co.uk/agilityClass/1799909160/running_orders"
response = requests.get(RunningOrdersURL)
RunningOrderSoup = BeautifulSoup(response.content, 'html.parser')
write_to_file(RunningOrderSoup, "NorthDerbyRunningOrders_LgeJmp.txt")
