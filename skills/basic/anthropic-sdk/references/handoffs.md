# Multi-Agent Orchestration

The Anthropic SDK has no built-in handoff mechanism. You orchestrate agents explicitly: call Claude, inspect the result, then decide what to call next. This gives you full control over routing, data passing, and error handling.

## Router Pattern

Classify intent with a fast call, then dispatch to the appropriate handler:

```python
import json
from anthropic import Anthropic

client = Anthropic()

INTENT_SCHEMA = {
    "type": "object",
    "properties": {
        "intent": {"type": "string", "enum": ["billing", "technical", "general"]},
    },
    "required": ["intent"],
}

def classify(user_message: str) -> str:
    response = client.messages.create(
        model="claude-opus-4-8",
        max_tokens=64,
        system=(
            "Classify the customer's request as: billing, technical, or general.\n"
            "billing — orders, refunds, invoices\n"
            "technical — errors, bugs, system issues\n"
            "general — everything else"
        ),
        messages=[{"role": "user", "content": user_message}],
        output_config={"format": {"type": "json_schema", "schema": INTENT_SCHEMA}},
    )
    return json.loads(response.content[0].text)["intent"]

def handle(user_message: str) -> str:
    intent = classify(user_message)
    if intent == "billing":
        return billing_agent(user_message)
    if intent == "technical":
        return technical_agent(user_message)
    return general_agent(user_message)
```

## Pipeline Pattern

Chain calls sequentially — each call receives the previous output:

```python
from anthropic import Anthropic

client = Anthropic()

def pipeline(raw_input: str) -> str:
    # Step 1: Extract key facts
    research = client.messages.create(
        model="claude-opus-4-8",
        max_tokens=512,
        system="Extract the 3 most important facts. Reply as a bullet list.",
        messages=[{"role": "user", "content": raw_input}],
    )
    facts = research.content[0].text

    # Step 2: Generate verdict from facts
    analysis = client.messages.create(
        model="claude-opus-4-8",
        max_tokens=256,
        system="Given these research facts, produce a one-paragraph investment verdict.",
        messages=[{"role": "user", "content": facts}],
    )
    return analysis.content[0].text
```

## Supervisor Pattern

A supervisor delegates sub-tasks to workers via tools:

```python
import json
from anthropic import Anthropic

client = Anthropic()

# Worker functions called by the supervisor via tool use
def news_summary(ticker: str) -> str:
    response = client.messages.create(
        model="claude-opus-4-8",
        max_tokens=256,
        system="Summarise recent news for this stock ticker in 3 bullet points.",
        messages=[{"role": "user", "content": ticker}],
    )
    return response.content[0].text

def financials_summary(ticker: str) -> str:
    response = client.messages.create(
        model="claude-opus-4-8",
        max_tokens=256,
        system="Summarise key financial metrics for this stock ticker.",
        messages=[{"role": "user", "content": ticker}],
    )
    return response.content[0].text

SUPERVISOR_TOOLS = [
    {
        "name": "get_news_summary",
        "description": "Get a news summary for a stock ticker.",
        "input_schema": {
            "type": "object",
            "properties": {"ticker": {"type": "string"}},
            "required": ["ticker"],
        },
    },
    {
        "name": "get_financials_summary",
        "description": "Get a financial metrics summary for a stock ticker.",
        "input_schema": {
            "type": "object",
            "properties": {"ticker": {"type": "string"}},
            "required": ["ticker"],
        },
    },
]

DISPATCH = {
    "get_news_summary": lambda inp: news_summary(**inp),
    "get_financials_summary": lambda inp: financials_summary(**inp),
}

def supervisor(user_message: str) -> str:
    messages = [{"role": "user", "content": user_message}]
    system = (
        "You are a research supervisor. Use your tools to gather news and financial data, "
        "then produce a comprehensive brief."
    )
    while True:
        response = client.messages.create(
            model="claude-opus-4-8",
            max_tokens=1024,
            system=system,
            tools=SUPERVISOR_TOOLS,
            messages=messages,
        )
        if response.stop_reason == "end_turn":
            return next((b.text for b in response.content if b.type == "text"), "")
        if response.stop_reason == "tool_use":
            messages.append({"role": "assistant", "content": response.content})
            results = [
                {"type": "tool_result", "tool_use_id": b.id, "content": DISPATCH[b.name](b.input)}
                for b in response.content if b.type == "tool_use"
            ]
            messages.append({"role": "user", "content": results})
```

## Parallel Workers

Run multiple agents concurrently with `asyncio.gather`:

```python
import asyncio
from anthropic import AsyncAnthropic

async_client = AsyncAnthropic()

async def worker(task: str, system: str) -> str:
    response = await async_client.messages.create(
        model="claude-opus-4-8",
        max_tokens=512,
        system=system,
        messages=[{"role": "user", "content": task}],
    )
    return response.content[0].text

async def parallel_research(ticker: str) -> str:
    news_task = worker(ticker, "Summarise recent news in 3 bullets.")
    fin_task  = worker(ticker, "Summarise key financial metrics in 3 bullets.")
    news, financials = await asyncio.gather(news_task, fin_task)

    # Synthesise
    combined = f"News:\n{news}\n\nFinancials:\n{financials}"
    synthesis = await async_client.messages.create(
        model="claude-opus-4-8",
        max_tokens=512,
        system="Combine the news and financial summaries into a one-page brief.",
        messages=[{"role": "user", "content": combined}],
    )
    return synthesis.content[0].text
```

## Passing Context Between Agents

Pass structured data as part of the next agent's user message:

```python
import json

def enrich_and_route(user_message: str, user_context: dict) -> str:
    # Summarise relevant context for the specialist
    context_str = json.dumps(user_context, indent=2)
    enriched = f"User context:\n{context_str}\n\nUser request:\n{user_message}"

    intent = classify(user_message)
    return specialist_map[intent](enriched)
```

## Choosing a Pattern

| Need | Pattern |
|---|---|
| Route to specialists by topic | Router |
| Sequential refinement steps | Pipeline |
| Parallel sub-tasks + synthesis | Parallel workers |
| Orchestrator delegates via tools | Supervisor |
| Collect structured data before routing | Router + `output_config` |
