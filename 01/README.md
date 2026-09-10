# LLM tool calling — beer planner

> **Zadání:** Napiš Python skript, který zavolá LLM API, použije nástroj
> (např. výpočetní funkci) a vrátí odpověď zpět LLM.

A minimal demonstration of **tool calling** (function calling): the model is asked a
question it cannot answer on its own, decides to call a Python function, receives the
function's return value, and turns it into a final answer.

The tool is `plan_beer()` — it works out how many bottles, whole crates and how many
crowns a party needs.

## How it works

```
  user question
       │
       ▼
  ①  POST /v1/chat/completions  (messages + tools)
       │
       ▼
     model replies with tool_calls: plan_beer(people=7, hours=6, thirst="high")
       │
       ▼
  ②  Python executes plan_beer() locally → {"bottles": 84, "crates": 4, ...}
       │
       ▼
  ③  POST /v1/chat/completions  (messages + {"role": "tool", "content": result})
       │
       ▼
     model replies in prose → final answer
```

Steps ① – ③ live in [`agent.py`](src/llm_tool_call/agent.py); the loop repeats until the
model answers without requesting another tool, or `LLM_MAX_TOOL_ROUNDS` is reached.

The model runs locally in **LM Studio**, which exposes an OpenAI-compatible API — so the
official `openai` SDK talks to it unchanged. Pointing `LLM_BASE_URL` at OpenAI, Groq or
OpenRouter instead works without touching the code.

## Prerequisites

- [uv](https://docs.astral.sh/uv/)
- [LM Studio](https://lmstudio.ai/) with `google/gemma-4-e4b` downloaded

Start the server and load the model:

```bash
lms server start
lms load google/gemma-4-e4b
```

The server listens on `http://localhost:1234`. Check it with `curl http://localhost:1234/v1/models`.

## Run

```bash
uv run llm-tool-call
```

with your own question:

```bash
uv run llm-tool-call "Máme firemní večírek, 24 lidí na 4 hodiny. Kolik beden piva?"
```

Example output:

```
Model:    google/gemma-4-e4b @ http://localhost:1234/v1
Question: Jedeme na chalupu, 7 lidí, 6 hodin, pořádná žízeň. Kolik piv koupit a za kolik?

  tool  plan_beer({"hours":6,"people":7,"thirst":"high"}) -> {"result": {"bottles": 84, "crates": 4, "spare_bottles": 4, "litres": 42.0, "price_czk": 2352}}

Answer:   Musíte koupit 84 lahví a 4 přepravky za celkem 2352 CZK.
```

The `tool` line is the whole point of the exercise: the model asked for `plan_beer`, Python
ran it, and the JSON on the right went back into the conversation as a `tool` message.

## Configuration

Everything has a working default, so no setup is needed for the local LM Studio case.
To change anything, copy `.env.example` to `.env`:

```bash
cp .env.example .env
```

| Variable              | Default                     | Meaning                             |
| --------------------- | --------------------------- | ----------------------------------- |
| `LLM_BASE_URL`        | `http://localhost:1234/v1`  | OpenAI-compatible endpoint          |
| `LLM_MODEL`           | `google/gemma-4-e4b`        | Model id from `GET /v1/models`      |
| `LLM_API_KEY`         | `lm-studio`                 | Ignored locally; real key if hosted |
| `LLM_MAX_TOOL_ROUNDS` | `5`                         | Safety stop for the tool loop       |

`.env` is git-ignored — only `.env.example` is committed, so no credentials end up in
the repository.

## Development

```bash
uv run pytest         # tests
uv run ruff check .   # lint
uv run ruff format .  # format
```

## Project structure

```
src/llm_tool_call/
  beer.py     tool implementation + the JSON Schema advertised to the model
  agent.py    chat-completions call and the tool-calling loop
  config.py   settings read from the environment
  cli.py      command-line entry point
tests/        unit tests for the tool and the tool dispatch
```

## Notes

Arguments arriving in a tool call are model output, i.e. untrusted input, so `plan_beer()`
validates them before doing any arithmetic. When a tool call fails, the error is passed
back to the model as the tool result instead of crashing the script — that gives the model
a chance to fix its own arguments and try again.

`gemma-4-e4b` is a small local model, so the wording of the final sentence varies between
runs and its Czech is occasionally clumsy. The numbers do not vary: they come from
`plan_beer()`, not from the model.
