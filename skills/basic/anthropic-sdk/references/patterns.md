# Multi-Agent Patterns

## Router Pattern

A classifier makes a quick structured decision, then the appropriate specialist runs:

```python
import json
from anthropic import Anthropic

client = Anthropic()

ROUTE_SCHEMA = {
    "type": "object",
    "properties": {
        "route": {"type": "string", "enum": ["billing", "technical", "general"]},
    },
    "required": ["route"],
}

def router(user_message: str) -> str:
    # Fast classification call
    clf = client.messages.create(
        model="claude-opus-4-8",
        max_tokens=64,
        system="Route to: billing (orders/refunds), technical (errors/bugs), general (other).",
        messages=[{"role": "user", "content": user_message}],
        output_config={"format": {"type": "json_schema", "schema": ROUTE_SCHEMA}},
    )
    route = json.loads(clf.content[0].text)["route"]

    specialists = {
        "billing":   billing_agent,
        "technical": technical_agent,
        "general":   general_agent,
    }
    return specialists[route](user_message)
```

## Pipeline Pattern

Chain agents sequentially — each output becomes the next input:

```python
from anthropic import Anthropic

client = Anthropic()

def call(system: str, user: str, max_tokens: int = 512) -> str:
    r = client.messages.create(
        model="claude-opus-4-8",
        max_tokens=max_tokens,
        system=system,
        messages=[{"role": "user", "content": user}],
    )
    return r.content[0].text

def research_pipeline(company: str) -> str:
    facts   = call("Summarise 3 key facts about the company.", company)
    verdict = call("Given these facts, write a one-paragraph investment verdict.", facts)
    report  = call("Format this verdict as a professional one-page report with header and bullet risks.", verdict, max_tokens=1024)
    return report
```

## Supervisor Pattern

A supervisor delegates sub-tasks to workers via tools and synthesises the results:

```python
import json
from anthropic import Anthropic

client = Anthropic()

def worker_call(system: str, user: str) -> str:
    r = client.messages.create(
        model="claude-opus-4-8",
        max_tokens=256,
        system=system,
        messages=[{"role": "user", "content": user}],
    )
    return r.content[0].text

SUPERVISOR_TOOLS = [
    {
        "name": "get_news",
        "description": "Get a news summary for a ticker.",
        "input_schema": {"type": "object", "properties": {"ticker": {"type": "string"}}, "required": ["ticker"]},
    },
    {
        "name": "get_financials",
        "description": "Get a financial summary for a ticker.",
        "input_schema": {"type": "object", "properties": {"ticker": {"type": "string"}}, "required": ["ticker"]},
    },
]

DISPATCH = {
    "get_news":       lambda inp: worker_call("Summarise recent news in 3 bullets.", inp["ticker"]),
    "get_financials": lambda inp: worker_call("Summarise key financial metrics in 3 bullets.", inp["ticker"]),
}

def supervisor(request: str) -> str:
    messages = [{"role": "user", "content": request}]
    while True:
        r = client.messages.create(
            model="claude-opus-4-8",
            max_tokens=1024,
            system="You are a research supervisor. Use tools to gather data, then write a brief.",
            tools=SUPERVISOR_TOOLS,
            messages=messages,
        )
        if r.stop_reason == "end_turn":
            return next((b.text for b in r.content if b.type == "text"), "")
        if r.stop_reason == "tool_use":
            messages.append({"role": "assistant", "content": r.content})
            results = [
                {"type": "tool_result", "tool_use_id": b.id, "content": DISPATCH[b.name](b.input)}
                for b in r.content if b.type == "tool_use"
            ]
            messages.append({"role": "user", "content": results})
```

## Structured Output from Any Agent

Use `output_config` to enforce a JSON schema:

```python
import json
from anthropic import Anthropic

client = Anthropic()

VERDICT_SCHEMA = {
    "type": "object",
    "properties": {
        "ticker":          {"type": "string"},
        "verdict":         {"type": "string", "enum": ["BUY", "HOLD", "SELL"]},
        "conviction":      {"type": "string", "enum": ["LOW", "MEDIUM", "HIGH"]},
        "one_line_reason": {"type": "string"},
    },
    "required": ["ticker", "verdict", "conviction", "one_line_reason"],
}

def get_verdict(ticker: str) -> dict:
    r = client.messages.create(
        model="claude-opus-4-8",
        max_tokens=256,
        system="Analyse the stock and return a structured verdict.",
        messages=[{"role": "user", "content": f"Evaluate {ticker}."}],
        output_config={"format": {"type": "json_schema", "schema": VERDICT_SCHEMA}},
    )
    return json.loads(r.content[0].text)

verdict = get_verdict("AAPL")
print(f"{verdict['ticker']}: {verdict['verdict']} ({verdict['conviction']}) — {verdict['one_line_reason']}")
```

## Map-Reduce Pattern

Map: run the same agent over many inputs in parallel. Reduce: synthesise.

```python
import asyncio
import json
from anthropic import AsyncAnthropic

async_client = AsyncAnthropic()

async def analyse_ticker(ticker: str) -> dict:
    r = await async_client.messages.create(
        model="claude-opus-4-8",
        max_tokens=128,
        system="Return a one-sentence summary and a BUY/HOLD/SELL rating.",
        messages=[{"role": "user", "content": ticker}],
        output_config={"format": {"type": "json_schema", "schema": {
            "type": "object",
            "properties": {
                "ticker":  {"type": "string"},
                "summary": {"type": "string"},
                "rating":  {"type": "string", "enum": ["BUY", "HOLD", "SELL"]},
            },
            "required": ["ticker", "summary", "rating"],
        }}},
    )
    return json.loads(r.content[0].text)

async def portfolio_screen(tickers: list[str]) -> str:
    # Map phase: analyse all tickers in parallel
    results = await asyncio.gather(*[analyse_ticker(t) for t in tickers])

    # Reduce phase: synthesise into a ranked list
    summaries = "\n".join(
        f"- {r['ticker']}: {r['rating']} — {r['summary']}"
        for r in results
    )
    synthesis = await async_client.messages.create(
        model="claude-opus-4-8",
        max_tokens=512,
        system="Rank these stocks from most to least attractive and explain.",
        messages=[{"role": "user", "content": summaries}],
    )
    return synthesis.content[0].text

# Usage
if __name__ == "__main__":
    print(asyncio.run(portfolio_screen(["AAPL", "NVDA", "MSFT", "GOOGL"])))
```

## Choosing a Pattern

| Need | Pattern |
|---|---|
| Route to specialists by topic | Router |
| Sequential refinement steps | Pipeline |
| Orchestrator + sub-tasks via tools | Supervisor |
| Same task over many inputs | Map-Reduce |
| Structured typed output | Any + `output_config` |
