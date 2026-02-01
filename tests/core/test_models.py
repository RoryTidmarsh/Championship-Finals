import pytest
from bs4 import BeautifulSoup
from src.core.models import *

# Test ClassInfo initialization and attribute setting
@pytest.mark.parametrize(
    "class_type,class_number,order,running_orders_url,results_url",
    [
        ("Agility", 1, 2, "http://example.com/running_orders", "http://example.com/results"),
        ("Jumping", 3, 1, None, "http://example.com/results"),
        ("Agility", 2, 5, "http://example.com/running_orders", None),
        ("Jumping", 4, 10, None, None),
    ],
)
def test_class_info_initialization(class_type, class_number, order, running_orders_url, results_url):
    class_info = ClassInfo(class_type=class_type, class_number=class_number, order=order,
                           running_orders_url=running_orders_url,
                           results_url=results_url)
    
    assert class_info.class_type == class_type
    assert class_info.class_number == class_number
    assert class_info.order == order
    assert class_info.running_orders_url == running_orders_url
    assert class_info.results_url == results_url
    assert class_info.status is None
    assert class_info.eliminations == []
    assert class_info.results_df is None
    assert class_info.running_orders_df is None

# Test invalid initialization of ClassInfo
@pytest.mark.parametrize(
    "class_type,class_number,order,running_orders_url,results_url,expected_exception",
    [
        # Invalid class_type - wrong value
        ("Speed", 1, 1, None, None, ValueError),
        ("Agil", 1, 1, None, None, ValueError),
        ("", 1, 1, None, None, ValueError),
        # Invalid class_type - wrong type
        (123, 1, 1, None, None, TypeError),
        (None, 1, 1, None, None, TypeError),
        # Invalid class_number - wrong type
        ("Agility", "1", 1, None, None, TypeError),
        ("Agility", 1.5, 1, None, None, TypeError),
        # ("Agility", None, 1, None, None, TypeError),
        # Invalid order - wrong type
        ("Agility", 1, "1", None, None, TypeError),
        ("Agility", 1, 1.5, None, None, TypeError),
        ("Agility", 1, None, None, None, TypeError),
        # Invalid running_orders_url - wrong type
        ("Agility", 1, 1, 123, None, TypeError),
        # Invalid results_url - wrong type
        ("Agility", 1, 1, None, 123, TypeError),
    ],
)
def test_class_info_invalid_initialization(class_type, class_number, order, 
                                          running_orders_url, results_url, 
                                          expected_exception):
    with pytest.raises(expected_exception):
        ClassInfo(class_type=class_type, class_number=class_number, order=order,
                 running_orders_url=running_orders_url, results_url=results_url)

# Test ClassInfo __repr__ method
def test_class_info_repr():
    class_info = ClassInfo(class_type="Jumping", class_number=2)
    class_info.results_df = [1, 2, 3]  # Mocking a DataFrame with a list for simplicity
    class_info.eliminations = ["bob", 102]
    repr_str = repr(class_info)
    assert "class_type=Jumping" in repr_str
    assert "results_df=3 rows" in repr_str
    assert "eliminations=2" in repr_str


# Test ClassInfo update_status method
@pytest.mark.parametrize(
    "running_orders_url,results_url,expected_status",
    [
        ("http://example.com/running_orders", "http://example.com/results", "in progress"),
        (None, "http://example.com/results", "completed"),
        ("http://example.com/running_orders", None, "not started"),
        (None, None, "not started, no running orders"),
    ],
)
def test_class_info_update_status(running_orders_url, results_url, expected_status):
    class_info = ClassInfo(class_type="Agility", class_number=1,
                           running_orders_url=running_orders_url,
                           results_url=results_url)
    class_info.update_status()
    assert class_info.status == expected_status
