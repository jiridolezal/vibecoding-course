import json
from types import SimpleNamespace

from llm_tool_call.agent import _execute


def make_tool_call(name: str, arguments: str) -> SimpleNamespace:
    return SimpleNamespace(id="call_1", function=SimpleNamespace(name=name, arguments=arguments))


def test_returns_tool_result_as_json() -> None:
    result = _execute(make_tool_call("plan_beer", '{"people": 7, "hours": 6, "thirst": "high"}'))
    assert json.loads(result)["result"]["bottles"] == 84


def test_reports_invalid_arguments_to_the_model_instead_of_raising() -> None:
    result = _execute(make_tool_call("plan_beer", '{"people": 0, "hours": 6}'))
    assert "People must be" in json.loads(result)["error"]


def test_reports_malformed_json_to_the_model_instead_of_raising() -> None:
    result = _execute(make_tool_call("plan_beer", "{not json"))
    assert "error" in json.loads(result)


def test_reports_unknown_tool_to_the_model_instead_of_raising() -> None:
    result = _execute(make_tool_call("delete_everything", "{}"))
    assert "error" in json.loads(result)
