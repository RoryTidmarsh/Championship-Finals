from pathlib import Path

import pytest
from bs4 import BeautifulSoup

import src.core.plaza_scraper as ps

HTML_FIXTURE = (Path(__file__).parent.parent / "fixtures" / "2025.html").read_text(
    encoding="utf-8"
)


@pytest.mark.parametrize(
    "show_name,show_date,expected_url",
    [
        (
            "North Derbyshire",
            "2025/09/13",
            "https://www.agilityplaza.co.uk/competition/1205629450/results",
        ),
        (
            "Wyre",
            "2025-09-20",
            "https://www.agilityplaza.co.uk/competition/2073145146/results",
        ),
        (
            "Kennel Club International Agility Festival",
            "2025-08-07",
            "https://www.agilityplaza.co.uk/competition/1224271619/results",
        ),
        (
            "kciaf",
            "2025-08-07",
            "https://www.agilityplaza.co.uk/competition/1224271619/results",
        ),
        (
            "dinas",
            "2025-08-12",
            "https://www.agilityplaza.co.uk/competition/1950031424/results",
        ),
        (
            "Gillingham",
            "2025-08-30",
            "https://www.agilityplaza.co.uk/competition/1723469670/results",
        ),
    ],
)
def test_find_show_url_success(monkeypatch, show_name, show_date, expected_url):
    soup = BeautifulSoup(HTML_FIXTURE, "html.parser")
    monkeypatch.setattr(ps, "get_soup", lambda url: soup)

    result = ps.find_show_url(show_name, show_date)
    assert result == expected_url, f"expected: {expected_url}, got {expected_url}"


@pytest.mark.parametrize(
    "show_name,show_date",
    [
        ("Fake Show Name", "2025/09/13"),
        ("kciaf", "2025/01/01"),
        (
            "Gillingham",
            "2025-30-08",
        ),
    ],
)
def test_find_show_url_not_found(monkeypatch, show_name, show_date):
    soup = BeautifulSoup(HTML_FIXTURE, "html.parser")
    monkeypatch.setattr(ps, "get_soup", lambda url: soup)

    with pytest.raises(ValueError):
        ps.find_show_url(show_name, show_date)


@pytest.mark.parametrize(
    "show_name,show_date",
    [
        (123, "2025/09/13"),
        (None, "2025/09/13"),
        ("North Derbyshire", 2025),
        ("North Derbyshire", None),
    ],
)
def test_find_show_url_invalid_types(monkeypatch, show_name, show_date):
    soup = BeautifulSoup(HTML_FIXTURE, "html.parser")
    monkeypatch.setattr(ps, "get_soup", lambda url: soup)

    with pytest.raises(AssertionError):
        ps.find_show_url(show_name, show_date)

# Test HTML scenarios
HTML_FIXTURE_1CLASS = (Path(__file__).parent.parent / "fixtures" / "findClass_oneClass.html").read_text(
    encoding="utf-8"
)
HTML_FIXTURE_2CLASS = (Path(__file__).parent.parent / "fixtures" / "findClass_twoClasses.html").read_text(
    encoding="utf-8"
)
HTML_FIXTURE_FINISHED = (Path(__file__).parent.parent / "fixtures" / "findClass_twoClassesFinished.html").read_text(
    encoding="utf-8"
)

HTML_FIXTURE_NOT_STARTED = (Path(__file__).parent.parent / "fixtures" / "findClass_runningOrdersOnly.html").read_text(
    encoding="utf-8"
)
@pytest.mark.parametrize(
    "html_fixture,agility_status,jumping_status,agility_order,jumping_order,agility_results_url,jumping_results_url, agility_ro_url, jumping_ro_url",
    [
        (
         HTML_FIXTURE_1CLASS, #html fixture
         "in progress",  #expected agility status
         "not started",  #expected jumping status
         0,
         1,
         "https://www.agilityplaza.co.uk/agilityClass/1263911657/results",
         None,
         "https://www.agilityplaza.co.uk/agilityClass/1263911657/running_orders",
         "https://www.agilityplaza.co.uk/agilityClass/1799909160/running_orders"        
        ),
        (
         HTML_FIXTURE_2CLASS, 
         "completed", 
         "in progress",
         0,
         1,
         "https://www.agilityplaza.co.uk/agilityClass/1263911657/results",
         "https://www.agilityplaza.co.uk/agilityClass/1799909160/results",
         None,
         "https://www.agilityplaza.co.uk/agilityClass/1799909160/running_orders"        
        ),
        (
         HTML_FIXTURE_FINISHED, 
         "completed", 
         "completed",
         2,
         2,
         "https://www.agilityplaza.co.uk/agilityClass/1263911657/results",
         "https://www.agilityplaza.co.uk/agilityClass/1799909160/results",
         None,
         None        
        ),
        (
            HTML_FIXTURE_NOT_STARTED,
            "not started",
            "not started",
            2,
            2,
            None,
            None,
            "https://www.agilityplaza.co.uk/agilityClass/1263911657/running_orders",
            "https://www.agilityplaza.co.uk/agilityClass/1799909160/running_orders"
        )
        
        
    ],
    ids=[
        "one-class-in-progress",
        "two-classes-jumping-in-progress",
        "two-classes-completed",
        "two-classes-not-started"
    ],
)
def test_find_champ_classes_valid(html_fixture, agility_status, jumping_status, agility_order, jumping_order, agility_results_url, jumping_results_url, agility_ro_url, jumping_ro_url):

    soup = BeautifulSoup(html_fixture, "html.parser")
    result = ps.find_champ_classes(soup, "Lge")
    assert type(result) == tuple

    agility,jumping = result

    # Check tuple returns in correct order
    assert agility.class_type == "Agility", "expected agility class first in tuple"
    assert jumping.class_type == "Jumping", "expected jumping class second in tuple"

    # Check status
    assert agility.status == agility_status, f"agility status expected '{agility_status}', got {agility.status}"
    assert jumping.status == jumping_status, f"jumping status expected '{jumping_status}', got {jumping.status}"

    # Check order
    assert agility.order == agility_order, f"agility order expected '{agility_order}', got {agility.order}"
    assert jumping.order == jumping_order, f"jumping order expected '{jumping_order}', got {jumping.order}"

    # Check results URLs
    assert agility.results_url == agility_results_url, f"agility results URL expected '{agility_results_url}', got {agility.results_url}"
    assert jumping.results_url == jumping_results_url, f"jumping results URL expected '{jumping_results_url}', got {jumping.results_url}"

    # Check running orders URLs
    assert agility.running_orders_url == agility_ro_url, f"agility running orders URL expected '{agility_ro_url}', got {agility.running_orders_url}"
    assert jumping.running_orders_url == jumping_ro_url, f"jumping running orders URL expected '{jumping_ro_url}', got {jumping.running_orders_url}"    

HTML_FIXTURE_INVALID = (Path(__file__).parent.parent / "fixtures" / "findClass_noLargeChampionship.html").read_text(
    encoding="utf-8"
)

def test_find_champ_classes_invalid_soup():
    soup = BeautifulSoup(HTML_FIXTURE_INVALID, "html.parser")
    with pytest.raises(ValueError):
        ps.find_champ_classes(soup, "Lge")

def test_find_champ_classes_valid_height_capitalisation():
    soup = BeautifulSoup(HTML_FIXTURE_1CLASS, "html.parser")
    result = ps.find_champ_classes(soup, "lge")
    assert type(result) == tuple, "Expected function to return a tuple. error arises from capitalisation not being managed correctly. (it shouldn't matter if height is 'Lge' or 'lge')"

@pytest.mark.parametrize(
    "html_fixture,height,error",
    [
        (HTML_FIXTURE_1CLASS, "Sml",ValueError), #height not at the show
        (HTML_FIXTURE_1CLASS, 123, TypeError), #height not a string
        (HTML_FIXTURE_1CLASS, None, TypeError), #height not a string
        (HTML_FIXTURE_1CLASS, "bananana", ValueError), #height not in height list
    ],
    ids=[
        "height-not-at-show",
        "height-not-string",
        "height-not-string-none",
        "height-not-in-list"
    ]
)
def test_find_champ_classes_invalid_heights(html_fixture, height, error):
    soup = BeautifulSoup(html_fixture, "html.parser")
    with pytest.raises(error):
        ps.find_champ_classes(soup, height)

def test_find_champ_classes_no_classes():
    soup = BeautifulSoup(HTML_FIXTURE_INVALID, "html.parser")
    with pytest.raises(ValueError):
        ps.find_champ_classes(soup, "Lge")


### Find Champ Class from IDs test
@pytest.mark.parametrize(
    "agilityID,jumpingID,expected_ag_url,expected_jump_url",
    [
        (
            1234567890,
            9876543210,
            "https://www.agilityplaza.co.uk/agilityClass/1234567890/results",
            "https://www.agilityplaza.co.uk/agilityClass/9876543210/results",
        ),
        (
            "123456890",
            "9876543210",
            "https://www.agilityplaza.co.uk/agilityClass/123456890/results",
            "https://www.agilityplaza.co.uk/agilityClass/9876543210/results",
        )
    ],
    ids=[
        "IDs as integers",
        "IDs as strings"
    ]
)
def test_find_champClass_fromIDs_valid(agilityID, jumpingID, expected_ag_url, expected_jump_url):
    result = ps.find_champClass_fromIDs(agilityID, jumpingID)
    assert type(result) == dict, "Expected function to return a dictionary."
    
    agility_url = result["agility_url"]
    jumping_url = result["jumping_url"]

    assert agility_url == expected_ag_url, f"Expected agility URL '{expected_ag_url}', got '{agility_url}'"
    assert jumping_url == expected_jump_url, f"Expected jumping URL '{expected_jump_url}', got '{jumping_url}'"

@pytest.mark.parametrize(
    "agilityID,jumpingID",
    [
        (None, 9876543210), #agilityID not provided
        (1234567890, None), #jumpingID not provided
        ("notanumber", 9876543210), #agilityID not a number
        (1234567890, "notanumber"), #jumpingID not a number
        (123, 9876543210), #agilityID not 10 digits
        (1234567890, 123), #jumpingID not 10 digits
    ],
    ids=[
        "agilityID-none",
        "jumpingID-none",
        "agilityID-not-number",
        "jumpingID-not-number",
        "agilityID-not-10-digits",
        "jumpingID-not-10-digits"
    ]
)
def test_find_champClass_fromIDs_invalid(agilityID, jumpingID):
    with pytest.raises(AssertionError):
        ps.find_champClass_fromIDs(agilityID, jumpingID)