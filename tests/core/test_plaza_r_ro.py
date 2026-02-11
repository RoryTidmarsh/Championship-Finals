import src.core.plaza_R_RO as RRO
from src.core.models import ClassInfo, Final
import pytest


@pytest.mark.parametrize(
    "text_fixture, expected_output",
    [
        (
            ": Firstname1 Lastname1 &amp; Dog1,  Firstname2 Lastname2 &amp; Dog2,",
            ["Firstname1 Lastname1 & Dog1", "Firstname2 Lastname2 & Dog2"],
        ),
        (
            "Eliminations: Firstname1 Lastname1 &amp; Dog1,  Firstname2 Lastname2 &amp; Dog2,",
            ["Firstname1 Lastname1 & Dog1", "Firstname2 Lastname2 & Dog2"],
        ),
        (
            "",
            [],
        ),
        (
            "Firstname1 Lastname1 &amp; Dog1 (R), Firstname2 Lastname2 &amp; Dog2 (5),",
            ["Firstname1 Lastname1 & Dog1", "Firstname2 Lastname2 & Dog2"],
        ),
        (
            "Firstname1 Lastname1 &amp; Dog1 (R,5), Firstname2 Lastname2 &amp; Dog2 (5,5),",
            ["Firstname1 Lastname1 & Dog1", "Firstname2 Lastname2 & Dog2"],
        ),
        (
            "Firstname1 Lastname1 &amp; Dog1 (R,R,R), Firstname2 Lastname2 &amp; Dog2 (5,5,5),",
            ["Firstname1 Lastname1 & Dog1", "Firstname2 Lastname2 & Dog2"],
        ),
        (
            "Firstname1 Lastname1 &amp; Dog1 (H), Firstname2 Lastname2 &amp; Dog2 (5),",
            ["Firstname1 Lastname1 & Dog1", "Firstname2 Lastname2 & Dog2"],
        ),
    ],
    ids=[
        "clear elimination",
        "elimination with 'Eliminations:' prefix",
        "empty string",
        "(R), (5) faults",
        "(R,5), (5,5) faults",
        "(R,R,R), (5,5,5) faults",
        "(H), (5) faults",
    ],
)
def test_process_eliminations(text_fixture, expected_output):
    result = RRO.process_eliminations(text_fixture)
    assert type(result) == list, f"Expected type list but got {type(result)}"
    assert result == expected_output, f"Expected {expected_output} but got {result}"
