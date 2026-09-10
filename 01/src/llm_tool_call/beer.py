"""The tool exposed to the model: how much beer to buy for a party.

Arguments come from the model, so they are untrusted input and get validated
before any arithmetic happens.
"""

import math

BOTTLE_LITRES = 0.5
CRATE_SIZE = 20  # bottles per crate ("bedna")
PRICE_PER_BOTTLE_CZK = 28

#: Bottles one person drinks per hour, by declared level of thirst.
THIRST_RATES = {"low": 0.5, "normal": 1.0, "high": 2.0}

MAX_PEOPLE = 500
MAX_HOURS = 24


class BeerPlannerError(ValueError):
    """The requested party does not make sense."""


def plan_beer(people: int, hours: float, thirst: str = "normal") -> dict:
    """Work out how much beer a party needs, rounded up to whole bottles."""
    if not 1 <= people <= MAX_PEOPLE:
        raise BeerPlannerError(f"People must be between 1 and {MAX_PEOPLE}, got {people}.")
    if not 0 < hours <= MAX_HOURS:
        raise BeerPlannerError(f"Hours must be between 0 and {MAX_HOURS}, got {hours}.")
    if thirst not in THIRST_RATES:
        raise BeerPlannerError(f"Thirst must be one of {sorted(THIRST_RATES)}, got {thirst!r}.")

    bottles = math.ceil(people * hours * THIRST_RATES[thirst])
    crates, spare_bottles = divmod(bottles, CRATE_SIZE)
    return {
        "bottles": bottles,
        "crates": crates,
        "spare_bottles": spare_bottles,
        "litres": round(bottles * BOTTLE_LITRES, 2),
        "price_czk": bottles * PRICE_PER_BOTTLE_CZK,
    }


#: JSON Schema advertised to the model in the `tools` parameter.
PLAN_BEER_TOOL = {
    "type": "function",
    "function": {
        "name": "plan_beer",
        "description": (
            "Calculate how much beer to buy for a party: number of bottles, whole crates "
            "and the total price in CZK. Always use this tool instead of estimating yourself."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "people": {
                    "type": "integer",
                    "description": "How many people are drinking.",
                },
                "hours": {
                    "type": "number",
                    "description": "How long the party lasts, in hours.",
                },
                "thirst": {
                    "type": "string",
                    "enum": sorted(THIRST_RATES),
                    "description": "How thirsty the crowd is. Defaults to 'normal'.",
                },
            },
            "required": ["people", "hours"],
        },
    },
}
