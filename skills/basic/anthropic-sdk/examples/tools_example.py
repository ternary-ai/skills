"""
Function Tools Example

Demonstrates various patterns for defining and dispatching tools
with the Anthropic SDK.
"""

import asyncio
import json
from anthropic import Anthropic, AsyncAnthropic

client = Anthropic()
async_client = AsyncAnthropic()


# ============================================================
# Tool Schema Helpers
# ============================================================

def make_tool(name: str, description: str, properties: dict, required: list[str]) -> dict:
    """Helper to build a tool definition dict."""
    return {
        "name": name,
        "description": description,
        "input_schema": {
            "type": "object",
            "properties": properties,
            "required": required,
        },
    }


# ============================================================
# Basic Tools
# ============================================================

ADD_TOOL = make_tool(
    name="add_numbers",
    description="Add two numbers together.",
    properties={
        "a": {"type": "number", "description": "First number."},
        "b": {"type": "number", "description": "Second number."},
    },
    required=["a", "b"],
)

FORMAT_CURRENCY_TOOL = make_tool(
    name="format_currency",
    description="Format a number as currency.",
    properties={
        "amount": {"type": "number", "description": "The monetary amount."},
        "currency": {
            "type": "string",
            "enum": ["USD", "EUR", "GBP"],
            "description": "Currency code.",
        },
    },
    required=["amount"],
)


def add_numbers(a: float, b: float) -> str:
    return str(a + b)


def format_currency(amount: float, currency: str = "USD") -> str:
    symbols = {"USD": "$", "EUR": "€", "GBP": "£"}
    return f"{symbols.get(currency, currency)}{amount:,.2f}"


# ============================================================
# Complex Object Tools
# ============================================================

VALIDATE_ADDRESS_TOOL = make_tool(
    name="validate_address",
    description="Validate a mailing address.",
    properties={
        "address": {
            "type": "object",
            "properties": {
                "street": {"type": "string"},
                "city": {"type": "string"},
                "state": {"type": "string"},
                "zip_code": {"type": "string"},
            },
            "required": ["street", "city", "state", "zip_code"],
            "description": "Mailing address to validate.",
        }
    },
    required=["address"],
)

PLACE_ORDER_TOOL = make_tool(
    name="place_order",
    description="Place a new order.",
    properties={
        "customer_id": {"type": "string"},
        "items": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "product_id": {"type": "string"},
                    "quantity": {"type": "integer", "minimum": 1},
                    "price": {"type": "number", "exclusiveMinimum": 0},
                },
                "required": ["product_id", "quantity", "price"],
            },
        },
        "shipping_address": {"type": "string"},
    },
    required=["customer_id", "items", "shipping_address"],
)


def validate_address(address: dict) -> str:
    is_valid = bool(address.get("zip_code") and len(address["zip_code"]) == 5)
    return json.dumps({
        "valid": is_valid,
        "normalized": {
            "street": address["street"].title(),
            "city": address["city"].title(),
            "state": address["state"].upper(),
            "zip_code": address["zip_code"],
        },
    })


def place_order(customer_id: str, items: list[dict], shipping_address: str) -> str:
    import uuid
    from datetime import datetime, timedelta
    total = sum(i["quantity"] * i["price"] for i in items)
    delivery = (datetime.now() + timedelta(days=5)).strftime("%Y-%m-%d")
    return json.dumps({
        "order_id": f"ORD-{uuid.uuid4().hex[:8].upper()}",
        "customer_id": customer_id,
        "total": total,
        "estimated_delivery": delivery,
    })


# ============================================================
# Async Tools
# ============================================================

FETCH_WEATHER_TOOL = make_tool(
    name="fetch_weather",
    description="Fetch current weather for a city.",
    properties={"city": {"type": "string", "description": "City name."}},
    required=["city"],
)

FETCH_STOCK_TOOL = make_tool(
    name="fetch_stock_price",
    description="Fetch current stock price for a ticker symbol.",
    properties={"symbol": {"type": "string", "description": "Stock ticker symbol."}},
    required=["symbol"],
)


async def fetch_weather(city: str) -> str:
    await asyncio.sleep(0.05)
    return json.dumps({"city": city, "temperature": 72, "condition": "Sunny", "humidity": 45})


async def fetch_stock_price(symbol: str) -> str:
    await asyncio.sleep(0.05)
    prices = {"AAPL": 178.50, "GOOGL": 142.30, "MSFT": 378.90}
    return json.dumps({"symbol": symbol.upper(), "price": prices.get(symbol.upper(), 100.00), "currency": "USD"})


# ============================================================
# Enum Parameter Tools
# ============================================================

SET_PRIORITY_TOOL = make_tool(
    name="set_priority",
    description="Set the priority of an item.",
    properties={
        "item_id": {"type": "string"},
        "priority": {"type": "string", "enum": ["low", "medium", "high", "critical"]},
    },
    required=["item_id", "priority"],
)

SEARCH_PRODUCTS_TOOL = make_tool(
    name="search_products",
    description="Search for products in the catalog.",
    properties={
        "query": {"type": "string"},
        "category": {
            "type": "string",
            "enum": ["electronics", "clothing", "home", "all"],
            "description": "Product category filter.",
        },
        "sort_by": {
            "type": "string",
            "enum": ["price", "rating", "newest"],
        },
        "limit": {"type": "integer", "minimum": 1, "maximum": 50},
    },
    required=["query"],
)


def set_priority(item_id: str, priority: str) -> str:
    values = {"low": 1, "medium": 2, "high": 3, "critical": 4}
    return json.dumps({"item_id": item_id, "priority": priority, "priority_value": values[priority]})


def search_products(query: str, category: str = "all", sort_by: str = "rating", limit: int = 10) -> str:
    results = [
        {"id": f"PROD-{i}", "name": f"{query} Product {i}", "price": 29.99 + i * 10, "rating": 4.5 - i * 0.1}
        for i in range(min(limit, 5))
    ]
    return json.dumps(results)


# ============================================================
# Tool Dispatch
# ============================================================

SYNC_DISPATCH = {
    "add_numbers": lambda inp: add_numbers(**inp),
    "format_currency": lambda inp: format_currency(**inp),
    "validate_address": lambda inp: validate_address(**inp),
    "place_order": lambda inp: place_order(**inp),
    "set_priority": lambda inp: set_priority(**inp),
    "search_products": lambda inp: search_products(**inp),
}

ASYNC_DISPATCH = {
    "fetch_weather": lambda inp: fetch_weather(**inp),
    "fetch_stock_price": lambda inp: fetch_stock_price(**inp),
}


def dispatch_tool(name: str, tool_input: dict) -> str:
    if name in SYNC_DISPATCH:
        try:
            return str(SYNC_DISPATCH[name](tool_input))
        except Exception as e:
            return json.dumps({"error": str(e)})
    return json.dumps({"error": f"Unknown tool: {name}"})


async def dispatch_tool_async(name: str, tool_input: dict) -> str:
    if name in ASYNC_DISPATCH:
        try:
            return await ASYNC_DISPATCH[name](tool_input)
        except Exception as e:
            return json.dumps({"error": str(e)})
    return dispatch_tool(name, tool_input)


# ============================================================
# Agent Runner Helpers
# ============================================================

def run_with_tools(user_message: str, tools: list[dict], system: str = "") -> str:
    """Synchronous tool-use loop."""
    messages = [{"role": "user", "content": user_message}]
    while True:
        response = client.messages.create(
            model="claude-opus-4-8",
            max_tokens=1024,
            system=system,
            tools=tools,
            messages=messages,
        )
        if response.stop_reason == "end_turn":
            return next((b.text for b in response.content if b.type == "text"), "")
        if response.stop_reason == "tool_use":
            messages.append({"role": "assistant", "content": response.content})
            results = [
                {"type": "tool_result", "tool_use_id": b.id, "content": dispatch_tool(b.name, b.input)}
                for b in response.content if b.type == "tool_use"
            ]
            messages.append({"role": "user", "content": results})


async def run_with_tools_async(user_message: str, tools: list[dict], system: str = "") -> str:
    """Asynchronous tool-use loop."""
    messages = [{"role": "user", "content": user_message}]
    while True:
        response = await async_client.messages.create(
            model="claude-opus-4-8",
            max_tokens=1024,
            system=system,
            tools=tools,
            messages=messages,
        )
        if response.stop_reason == "end_turn":
            return next((b.text for b in response.content if b.type == "text"), "")
        if response.stop_reason == "tool_use":
            messages.append({"role": "assistant", "content": response.content})
            results = []
            for b in response.content:
                if b.type == "tool_use":
                    content = await dispatch_tool_async(b.name, b.input)
                    results.append({"type": "tool_result", "tool_use_id": b.id, "content": content})
            messages.append({"role": "user", "content": results})


# ============================================================
# Example Usage
# ============================================================

def calculator_example():
    print("=== Calculator Example ===\n")
    result = run_with_tools(
        "Add 1234.56 and 789.12, then format the result as EUR",
        tools=[ADD_TOOL, FORMAT_CURRENCY_TOOL],
        system="You are a calculator. Help with math and currency formatting.",
    )
    print(f"Result: {result}\n")


def ecommerce_example():
    print("=== E-Commerce Example ===\n")
    result = run_with_tools(
        "Search for wireless headphones, show top 3 by rating",
        tools=[SEARCH_PRODUCTS_TOOL, VALIDATE_ADDRESS_TOOL, PLACE_ORDER_TOOL],
        system="You help customers search products and place orders.",
    )
    print(f"Result: {result}\n")


async def async_tools_example():
    print("=== Async Tools Example ===\n")
    result = await run_with_tools_async(
        "What's the weather in San Francisco and the current price of AAPL?",
        tools=[FETCH_WEATHER_TOOL, FETCH_STOCK_TOOL],
        system="You fetch real-time data.",
    )
    print(f"Result: {result}\n")


def main():
    calculator_example()
    ecommerce_example()
    asyncio.run(async_tools_example())


if __name__ == "__main__":
    main()
