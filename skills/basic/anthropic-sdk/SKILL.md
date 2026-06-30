---
name: anthropic-sdk
description: Builds and modifies AI applications using the Anthropic Python SDK. Use when the user asks to create an AI agent, add tools, implement multi-agent pipelines, add input/output validation, build a routing agent, stream responses, or work with the anthropic package.
---

# Anthropic SDK

Install: `pip install anthropic`

## Quick start

```python
from anthropic import Anthropic

client = Anthropic()

response = client.messages.create(
    model="claude-opus-4-8",
    max_tokens=1024,
    messages=[{"role": "user", "content": "What is the capital of France?"}],
)
print(response.content[0].text)
```

## Core concepts

- **Client**: `Anthropic()` — reads `ANTHROPIC_API_KEY` from env
- **Messages**: `client.messages.create()` returns a `Message`; always set `max_tokens`
- **Tool use**: define tools as JSON schema dicts; Claude calls them, you execute and loop
- **Multi-turn**: maintain a `messages` list; append each turn manually
- **Streaming**: `client.messages.stream()` context manager
- **Thinking**: `thinking={"type": "adaptive"}` for complex reasoning (Opus 4.6+)

## Tool use

```python
from anthropic import Anthropic

client = Anthropic()

tools = [
    {
        "name": "get_stock_price",
        "description": "Return the current price of a stock.",
        "input_schema": {
            "type": "object",
            "properties": {
                "ticker": {"type": "string", "description": "Stock symbol."},
            },
            "required": ["ticker"],
        },
    }
]

def get_stock_price(ticker: str) -> str:
    return f"{ticker}: $100"

messages = [{"role": "user", "content": "What is AAPL trading at?"}]

while True:
    response = client.messages.create(
        model="claude-opus-4-8",
        max_tokens=1024,
        tools=tools,
        messages=messages,
    )
    if response.stop_reason == "end_turn":
        print(response.content[0].text)
        break
    if response.stop_reason == "tool_use":
        messages.append({"role": "assistant", "content": response.content})
        results = []
        for block in response.content:
            if block.type == "tool_use":
                output = get_stock_price(**block.input)
                results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": output,
                })
        messages.append({"role": "user", "content": results})
```

Tool schema patterns, error handling, complex types → See [references/tools.md](references/tools.md)

## Multi-turn conversation

```python
messages = []

def chat(user_msg: str) -> str:
    messages.append({"role": "user", "content": user_msg})
    response = client.messages.create(
        model="claude-opus-4-8",
        max_tokens=1024,
        messages=messages,
    )
    reply = response.content[0].text
    messages.append({"role": "assistant", "content": reply})
    return reply
```

## Streaming

```python
with client.messages.stream(
    model="claude-opus-4-8",
    max_tokens=1024,
    messages=[{"role": "user", "content": "Tell me a story."}],
) as stream:
    for text in stream.text_stream:
        print(text, end="", flush=True)
```

Full streaming, `.get_final_message()`, conversation history → See [references/running.md](references/running.md)

## Multi-agent patterns

- **Pipeline**: chain `messages.create()` calls — output of one feeds the next
- **Router**: classify intent with a fast call, then dispatch to the right handler
- **Supervisor**: orchestrator calls worker functions via tools or direct invocations

Full examples with structured output → See [references/patterns.md](references/patterns.md)

## Input/output validation

```python
def run_with_validation(user_msg: str) -> str:
    check = client.messages.create(
        model="claude-opus-4-8",
        max_tokens=64,
        messages=[{
            "role": "user",
            "content": f"Is this appropriate for a support context? Reply YES or NO.\n\n{user_msg}",
        }],
    )
    if "NO" in check.content[0].text.upper():
        return "I can't process that request."

    response = client.messages.create(
        model="claude-opus-4-8",
        max_tokens=1024,
        messages=[{"role": "user", "content": user_msg}],
    )
    return response.content[0].text
```

Structured validation, JSON schema output, retry patterns → See [references/guardrails.md](references/guardrails.md)

## Best practices

- Always set `max_tokens` — the API requires it
- Use `thinking={"type": "adaptive"}` for complex reasoning on Opus 4.6+
- Append `response.content` (the full list) when using tools — not just the text block
- Return errors in `tool_result` `content` so Claude can recover gracefully
- Use streaming for long outputs to prevent timeouts
- Keep the `messages` list in scope for multi-turn; never mutate already-sent entries
