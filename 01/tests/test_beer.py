import pytest

from llm_tool_call.beer import BeerPlannerError, plan_beer


def test_plans_a_thirsty_weekend() -> None:
    assert plan_beer(people=7, hours=6, thirst="high") == {
        "bottles": 84,
        "crates": 4,
        "spare_bottles": 4,
        "litres": 42.0,
        "price_czk": 2352,
    }


def test_defaults_to_normal_thirst() -> None:
    assert plan_beer(people=4, hours=5) == plan_beer(people=4, hours=5, thirst="normal")


def test_rounds_partial_bottles_up() -> None:
    # 3 people * 1.5 h * 0.5 = 2.25 bottles — nobody sells a quarter bottle.
    assert plan_beer(people=3, hours=1.5, thirst="low")["bottles"] == 3


@pytest.mark.parametrize(
    ("kwargs", "message"),
    [
        ({"people": 0, "hours": 3}, "People must be"),
        ({"people": 10_000, "hours": 3}, "People must be"),
        ({"people": 5, "hours": 0}, "Hours must be"),
        ({"people": 5, "hours": 99}, "Hours must be"),
        ({"people": 5, "hours": 3, "thirst": "unquenchable"}, "Thirst must be"),
    ],
)
def test_rejects_nonsense_parties(kwargs: dict, message: str) -> None:
    with pytest.raises(BeerPlannerError, match=message):
        plan_beer(**kwargs)
