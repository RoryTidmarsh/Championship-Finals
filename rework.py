import requests
from bs4 import BeautifulSoup
import difflib
from urllib.parse import urljoin
import pandas as pd
import os

Target_show_name = "North Derbyshire Dog Agility Club"
# print(find_show_url("North Derbyshire Dog Agility Club", num_shows=30))

"""Now, use saved HTML from a running competition: North Derbyshire show
The files we have in `NorthDerbySaves` are:
 - NorthDerbyRunningOrders_LgeJmp.html: Running orders of large jump, 2nd champ round
 - NorhtDerbyShow_FirstClass.html: HTML of results page while only large agility is shown. This has results link to the first class and links to both running orders.
 - NorthDerbyShow_SecondClass.html: HTML file of the results page of ND show while the second round of champ is running. 
 - NorthDerbyShow_LgeAg_complete.html: HTML of large champ agility results (class finished)
 - NorthDerbyShow_LgeJmp_incomplete.html: HTML of large champ jumping results (class in progress).

 The 2 results files should be accessable from the `NorthDerbyShow_SecondClass.hrml` file. So start the code with that.
"""

if __name__ =="__main__":
    simulation_soup = read_from_file(os.path.join("NorthDerbySaves", "NorthDerbyShow_SecondClass.html"))
    agility_class, jumping_class = find_champ_classes(simulation_soup, 'Lge')
    # print(agility_class,"\n", jumping_class)

    # print(os.listdir( os.getcwd() +"//NorthDerbySaves"))
    jumping_class_results, jumping_class_eliminations = import_results(jumping_class, simulation=True)
    dummy_class = ClassInfo("dummy", results_url=None, running_orders_url=None)
    dummy_class.update_status()
    print(import_results(dummy_class, simulation=False))
    jumping_running_orders = Find_duplicates(import_running_orders(jumping_class, simulation=True))
    agility_running_orders = import_running_orders(agility_class, simulation=True)
