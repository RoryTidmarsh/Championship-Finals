import pytest
from bs4 import BeautifulSoup
import src.core.plaza_scraper as ps
from pathlib import Path

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
