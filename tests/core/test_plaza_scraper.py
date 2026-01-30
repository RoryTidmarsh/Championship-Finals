import pytest
from bs4 import BeautifulSoup
import src.core.plaza_scraper as ps
from pathlib import Path

HTML_FIXTURE = (Path(__file__).parent.parent / "fixtures" / "2025.html").read_text(
    encoding="utf-8"
)


@pytest.mark.parametrize(
    "show_name,show_date,expected_url,expected_exc",
    [
        (
            "North Derbyshire",
            "2025/09/13",
            "https://www.agilityplaza.co.uk/competition/1205629450/results",
            None,
        ),
        (
            "Wyre",
            "2025-09-20",
            "https://www.agilityplaza.co.uk/competition/2073145146/results",
            None,
        ),
        ("Fake Show Name", "2025/09/13", None, ValueError),
    ],
)
def test_find_show_url_cases(
    monkeypatch, show_name, show_date, expected_url, expected_exc
):
    soup = BeautifulSoup(HTML_FIXTURE, "html.parser")
    monkeypatch.setattr(ps, "get_soup", lambda url: soup)

    if expected_exc:
        with pytest.raises(expected_exc):
            ps.find_show_url(show_name, show_date)
    else:
        result = ps.find_show_url(show_name, show_date)
        assert result == expected_url
