# Running Agents — Advanced Patterns

## Shared Context

Pass data to tools via closure or by including it in the system prompt. For structured state, use a context dict captured by your tool functions:

```python
from anthropic import Anthropic

client = Anthropic()

def make_agent(user_context: dict):
    """Return an agent function with access to user_context via closure."""

    TOOLS = [
        {
            "name": "get_portfolio",
            "description": "Return the current user's portfolio.",
            "input_schema": {"type": "object", "properties": {}, "required": []},
        },
    ]

    def get_portfolio() -> str:
        return str(user_context.get("portfolio", {}))

    def run(user_message: str) -> str:
        messages = [{"role": "user", "content": user_message}]
        while True:
            r = client.messages.create(
                model="claude-opus-4-8",
                max_tokens=1024,
                tools=TOOLS,
                messages=messages,
            )
            if r.stop_reason == "end_turn":
                return next((b.text for b in r.content if b.type == "text"), "")
            if r.stop_reason == "tool_use":
                messages.append({"role": "assistant", "content": r.content})
                results = []
                for b in r.content:
                    if b.type == "tool_use" and b.name == "get_portfolio":
                        results.append({"type": "tool_result", "tool_use_id": b.id, "content": get_portfolio()})
                messages.append({"role": "user", "content": results})

    return run

ctx = {"user_id": "alice", "portfolio": {"AAPL": 10, "NVDA": 5}}
agent = make_agent(ctx)
print(agent("What do I own?"))
```

## Multi-Turn Conversation

Maintain a `messages` list across turns:

```python
from anthropic import Anthropic

client = Anthropic()

messages = []

def chat(user_message: str, system: str = "") -> str:
    messages.append({"role": "user", "content": user_message})
    kwargs = {"model": "claude-opus-4-8", "max_tokens": 1024, "messages": messages}
    if system:
        kwargs["system"] = system

    r = client.messages.create(**kwargs)
    reply = r.content[0].text
    messages.append({"role": "assistant", "content": reply})
    return reply

print(chat("My name is Alice."))
print(chat("What is my name?"))  # recalls "Alice"
```

For tool use in multi-turn conversations, append `response.content` (the full list) as the assistant turn — not just the text block — so tool_use blocks are preserved.

## Streaming

Use the `stream()` context manager for incremental output:

```python
from anthropic import Anthropic

client = Anthropic()

with client.messages.stream(
    model="claude-opus-4-8",
    max_tokens=1024,
    messages=[{"role": "user", "content": "Write a short story about a robot."}],
) as stream:
    for text in stream.text_stream:
        print(text, end="", flush=True)

print()  # newline after stream
```

Get the complete `Message` object after streaming:

```python
with client.messages.stream(
    model="claude-opus-4-8",
    max_tokens=1024,
    messages=[{"role": "user", "content": "Summarise Apple's Q1 earnings."}],
) as stream:
    for text in stream.text_stream:
        print(text, end="", flush=True)
    final = stream.get_final_message()   # full Message with usage stats

print(f"\nInput tokens:  {final.usage.input_tokens}")
print(f"Output tokens: {final.usage.output_tokens}")
```

## Structured Output

Use `output_config` to constrain Claude's response to a JSON schema:

```python
import json
from anthropic import Anthropic

client = Anthropic()

SUMMARY_SCHEMA = {
    "type": "object",
    "properties": {
        "headline":  {"type": "string"},
        "body":      {"type": "string"},
        "sentiment": {"type": "string", "enum": ["POSITIVE", "NEUTRAL", "NEGATIVE"]},
    },
    "required": ["headline", "body", "sentiment"],
}

r = client.messages.create(
    model="claude-opus-4-8",
    max_tokens=512,
    messages=[{"role": "user", "content": "Apple reported record revenue this quarter."}],
    output_config={"format": {"type": "json_schema", "schema": SUMMARY_SCHEMA}},
)
summary = json.loads(r.content[0].text)
print(summary["headline"], summary["sentiment"])
```

## Extended Thinking

Enable `thinking={"type": "adaptive"}` on Opus 4.6+ for complex tasks:

```python
from anthropic import Anthropic

client = Anthropic()

r = client.messages.create(
    model="claude-opus-4-8",
    max_tokens=8096,
    thinking={"type": "adaptive"},
    messages=[{"role": "user", "content": "What are the main risks in concentrating a portfolio in one sector?"}],
)

# thinking blocks come first, text block last
for block in r.content:
    if block.type == "text":
        print(block.text)
```

## Error Handling

```python
import anthropic

try:
    r = client.messages.create(
        model="claude-opus-4-8",
        max_tokens=1024,
        messages=[{"role": "user", "content": user_input}],
    )
    return r.content[0].text

except anthropic.BadRequestError as e:
    # Invalid input (e.g. content policy)
    return "I can't respond to that request."

except anthropic.RateLimitError:
    return "Rate limit reached. Please try again shortly."

except anthropic.APIConnectionError:
    return "Connection error. Please check your network and retry."

except anthropic.APIStatusError as e:
    # Unexpected 4xx/5xx
    return f"API error {e.status_code}: {e.message}"
```

## Synchronous Wrapper for Async Code

When you need a sync interface:

```python
import asyncio
from anthropic import AsyncAnthropic

async_client = AsyncAnthropic()

async def _async_ask(question: str) -> str:
    r = await async_client.messages.create(
        model="claude-opus-4-8",
        max_tokens=512,
        messages=[{"role": "user", "content": question}],
    )
    return r.content[0].text

def ask(question: str) -> str:
    return asyncio.run(_async_ask(question))

print(ask("What year was Python created?"))
```

## Token Counting

Count tokens before sending to estimate cost:

```python
from anthropic import Anthropic

client = Anthropic()

count = client.messages.count_tokens(
    model="claude-opus-4-8",
    messages=[{"role": "user", "content": "What is the capital of France?"}],
)
print(f"Input tokens: {count.input_tokens}")
```

## Usage Tracking

Access usage stats on every response:

```python
r = client.messages.create(
    model="claude-opus-4-8",
    max_tokens=1024,
    messages=[{"role": "user", "content": "Hello."}],
)
print(f"In: {r.usage.input_tokens}, Out: {r.usage.output_tokens}")
```
