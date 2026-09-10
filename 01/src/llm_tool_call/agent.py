"""Chat-completions loop: ask the model, run any tool it requests, feed the result back."""

import json
from collections.abc import Callable
from dataclasses import dataclass, field

from openai import OpenAI
from openai.types.chat import ChatCompletionMessageToolCall

from llm_tool_call.beer import PLAN_BEER_TOOL, plan_beer
from llm_tool_call.config import Settings

SYSTEM_PROMPT = (
    "You are a precise assistant. Use the provided tools for every calculation. "
    "Answer in one or two short sentences, quoting the tool's numbers exactly and "
    "keeping their units: bottles are bottles, crates are crates, prices are in CZK. "
    "Never invent a number the tool did not return. "
    "Always reply in the same language the user wrote in."
)

TOOLS = [PLAN_BEER_TOOL]
TOOL_FUNCTIONS: dict[str, Callable[..., object]] = {"plan_beer": plan_beer}


@dataclass(frozen=True)
class ToolCall:
    """A single tool invocation requested by the model, plus what it got back."""

    name: str
    arguments: str
    result: str


@dataclass(frozen=True)
class Answer:
    """The model's final reply and the trace of tools it used to get there."""

    text: str
    tool_calls: list[ToolCall] = field(default_factory=list)


def ask(question: str, settings: Settings) -> Answer:
    """Send `question` to the model and resolve tool calls until it answers in prose."""
    client = OpenAI(base_url=settings.base_url, api_key=settings.api_key)
    messages: list[dict] = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": question},
    ]
    trace: list[ToolCall] = []

    for _ in range(settings.max_tool_rounds):
        completion = client.chat.completions.create(
            model=settings.model,
            messages=messages,
            tools=TOOLS,
            tool_choice="auto",
        )
        message = completion.choices[0].message
        messages.append(message.model_dump(exclude_none=True))

        if not message.tool_calls:
            return Answer(text=(message.content or "").strip(), tool_calls=trace)

        for tool_call in message.tool_calls:
            result = _execute(tool_call)
            trace.append(ToolCall(tool_call.function.name, tool_call.function.arguments, result))
            messages.append({"role": "tool", "tool_call_id": tool_call.id, "content": result})

    raise RuntimeError(
        f"The model kept calling tools after {settings.max_tool_rounds} rounds without answering."
    )


def _execute(tool_call: ChatCompletionMessageToolCall) -> str:
    """Run one tool call and serialise its outcome for the model.

    Failures are reported back as data rather than raised, so the model can correct itself.
    """
    try:
        function = TOOL_FUNCTIONS[tool_call.function.name]
        arguments = json.loads(tool_call.function.arguments)
        return json.dumps({"result": function(**arguments)})
    except (KeyError, TypeError, ValueError) as exc:
        return json.dumps({"error": f"{type(exc).__name__}: {exc}"})
