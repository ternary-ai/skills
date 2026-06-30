# Tools Reference

## Tool Definition Format

Every tool is a dict with `name`, `description`, and `input_schema` (JSON Schema object):

```python
tool = {
    "name": "get_stock_price",
    "description": "Return the current price of a stock ticker.",
    "input_schema": {
        "type": "object",
        "properties": {
            "ticker": {"type": "string", "description": "Stock symbol, e.g. AAPL."},
        },
        "required": ["ticker"],
    },
}
```

Pass a list of tool dicts to `client.messages.create(tools=[...])`.

## Parameter Types

### Primitives

```python
"properties": {
    "text":    {"type": "string"},
    "count":   {"type": "integer"},
    "amount":  {"type": "number"},
    "enabled": {"type": "boolean"},
}
```

### Optional parameters

Omit the key from `required` to make it optional:

```python
"properties": {
    "query":    {"type": "string"},
    "limit":    {"type": "integer", "description": "Max results (default 10)."},
},
"required": ["query"],   # limit is optional
```

### Enums

```python
"priority": {
    "type": "string",
    "enum": ["low", "medium", "high", "critical"],
    "description": "Priority level.",
},
```

### Arrays

```python
"tickers": {
    "type": "array",
    "items": {"type": "string"},
    "description": "List of stock ticker symbols.",
},
```

### Nested objects

```python
"address": {
    "type": "object",
    "properties": {
        "street":   {"type": "string"},
        "city":     {"type": "string"},
        "zip_code": {"type": "string"},
    },
    "required": ["street", "city", "zip_code"],
},
```

### Array of objects

```python
"items": {
    "type": "array",
    "items": {
        "type": "object",
        "properties": {
            "product_id": {"type": "string"},
            "quantity":   {"type": "integer", "minimum": 1},
            "price":      {"type": "number", "exclusiveMinimum": 0},
        },
        "required": ["product_id", "quantity", "price"],
    },
},
```

## Tool Use Loop

```python
from anthropic import Anthropic

client = Anthropic()

def run_tools(user_message: str, tools: list[dict], dispatch: dict) -> str:
    """Generic tool-use loop. dispatch maps tool name → callable."""
    messages = [{"role": "user", "content": user_message}]

    while True:
        response = client.messages.create(
            model="claude-opus-4-8",
            max_tokens=1024,
            tools=tools,
            messages=messages,
        )

        if response.stop_reason == "end_turn":
            return next((b.text for b in response.content if b.type == "text"), "")

        if response.stop_reason == "tool_use":
            # Append the full assistant content (preserves tool_use blocks)
            messages.append({"role": "assistant", "content": response.content})

            results = []
            for block in response.content:
                if block.type == "tool_use":
                    try:
                        output = dispatch[block.name](**block.input)
                        content = str(output)
                    except Exception as e:
                        content = f"Error: {e}"
                    results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": content,
                    })
            messages.append({"role": "user", "content": results})
```

## Error Handling

Return a descriptive error string in `content` so Claude can inform the user:

```python
for block in response.content:
    if block.type == "tool_use":
        try:
            result = call_external_api(block.input)
            content = json.dumps(result)
        except requests.Timeout:
            content = "Error: request timed out. Please try again."
        except ValueError as e:
            content = f"Validation error: {e}"

        results.append({
            "type": "tool_result",
            "tool_use_id": block.id,
            "content": content,
        })
```

Never raise from inside the tool loop — it breaks the conversation. Catch and return.

## Returning Structured Data from Tools

Return JSON strings; Claude parses them naturally:

```python
import json

def lookup_order(order_id: str) -> str:
    order = db.get(order_id)
    if not order:
        return json.dumps({"error": "Order not found"})
    return json.dumps({"id": order.id, "status": order.status, "total": order.total})
```

## Async Tool Use

Use `AsyncAnthropic` and `await`:

```python
import asyncio
from anthropic import AsyncAnthropic

async_client = AsyncAnthropic()

async def run_tools_async(user_message: str, tools: list[dict], dispatch: dict) -> str:
    messages = [{"role": "user", "content": user_message}]

    while True:
        response = await async_client.messages.create(
            model="claude-opus-4-8",
            max_tokens=1024,
            tools=tools,
            messages=messages,
        )

        if response.stop_reason == "end_turn":
            return next((b.text for b in response.content if b.type == "text"), "")

        if response.stop_reason == "tool_use":
            messages.append({"role": "assistant", "content": response.content})
            # Run all tool calls in parallel
            tasks = [
                dispatch[b.name](**b.input)
                for b in response.content if b.type == "tool_use"
            ]
            outputs = await asyncio.gather(*tasks, return_exceptions=True)

            results = []
            tool_blocks = [b for b in response.content if b.type == "tool_use"]
            for block, output in zip(tool_blocks, outputs):
                content = str(output) if not isinstance(output, Exception) else f"Error: {output}"
                results.append({"type": "tool_result", "tool_use_id": block.id, "content": content})

            messages.append({"role": "user", "content": results})
```

## Organizing Tools

Group related tools and dispatch functions by domain:

```python
# tools/billing.py
BILLING_TOOLS = [lookup_order_tool, process_refund_tool]

BILLING_DISPATCH = {
    "lookup_order": lookup_order,
    "process_refund": process_refund,
}

# tools/technical.py
TECHNICAL_TOOLS = [check_status_tool, create_ticket_tool]

TECHNICAL_DISPATCH = {
    "check_system_status": check_system_status,
    "create_support_ticket": create_support_ticket,
}

# Merge for a combined agent
ALL_TOOLS = BILLING_TOOLS + TECHNICAL_TOOLS
ALL_DISPATCH = {**BILLING_DISPATCH, **TECHNICAL_DISPATCH}
```

## Best Practices

- Write clear, specific descriptions — they are the only documentation Claude sees
- List all required params explicitly; omit optional params from `required`
- Return JSON strings for structured data, plain strings for simple values
- Always catch exceptions in tool functions and return error strings
- Keep each tool focused on a single action
- Use enums to constrain string params to known values
