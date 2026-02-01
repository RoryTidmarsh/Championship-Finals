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

# Test ClassInfo update_order method
@pytest.mark.parametrize(
        "status1,status2,expected_order1,expected_order2",
    [
        ("completed", "completed", 2, 2),
        ("in progress", "in progress", 2, 2),
        ("not started", "not started", 2, 2),
        ("completed", "in progress", 0, 1),
        ("in progress", "not started", 0, 1),
        ("completed", "not started", 0, 1),
    ],
)
def test_class_info_update_order(status1, status2, expected_order1, expected_order2):
    class1 = ClassInfo(class_type="Agility")
    class2 = ClassInfo(class_type="Jumping")
    
    class1.status = status1
    class2.status = status2

    class1.update_order(class2)

    assert class1.order == expected_order1
    assert class2.order == expected_order2

# Test ClassInfo to_dict method
def test_class_info_to_dict_basic():
    class_info = ClassInfo(
        class_type="Agility",
        class_number=5,
        order=1,
        running_orders_url="http://example.com/ro",
        results_url="http://example.com/results"
    )
    class_info.status = "completed"
    class_info.classID = "ABC123"
    
    result = class_info.to_dict()
    
    assert result["class_type"] == "Agility"
    assert result["class_number"] == 5
    assert result["order"] == 1
    assert result["running_orders_url"] == "http://example.com/ro"
    assert result["results_url"] == "http://example.com/results"
    assert result["status"] == "completed"
    assert result["classID"] == "ABC123"
    assert result["eliminations_count"] == 0
    assert result["results_df_rows"] == 0


def test_class_info_to_dict_with_data():
    class_info = ClassInfo(class_type="Jumping", class_number=3)
    class_info.status = "in progress"
    class_info.eliminations = ["Dog1", "Dog2", "Dog3"]
    class_info.results_df = [1, 2, 3, 4, 5]  # Mock DataFrame as list with 5 items
    
    result = class_info.to_dict()
    
    assert result["class_type"] == "Jumping"
    assert result["eliminations_count"] == 3
    assert result["results_df_rows"] == 5


def test_class_info_to_dict_none_values():
    class_info = ClassInfo(class_type="Agility")
    
    result = class_info.to_dict()
    
    assert result["class_number"] is None
    assert result["running_orders_url"] is None
    assert result["results_url"] is None
    assert result["status"] is None
    assert result["classID"] is None
    assert result["eliminations_count"] == 0
    assert result["results_df_rows"] == 0

