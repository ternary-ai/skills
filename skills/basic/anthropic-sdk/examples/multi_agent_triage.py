"""
Multi-Agent Triage Example

Customer service system with intent routing and specialist handlers.
Uses a fast classifier call to route the user, then runs the appropriate
specialist with its own tool set.
"""

import json
from anthropic import Anthropic

client = Anthropic()


# ============================================================
# Simulated Data / Utilities
# ============================================================

ORDERS = {
    "ORD-001": {"id": "ORD-001", "status": "delivered", "total": 99.99, "items": ["Widget A"], "date": "2024-01-15"},
    "ORD-002": {"id": "ORD-002", "status": "shipped",   "total": 149.99, "items": ["Premium Widget"], "date": "2024-01-20"},
}

SYSTEM_STATUSES = {
    "api":      {"status": "operational", "latency_ms": 45},
    "database": {"status": "operational", "latency_ms": 12},
    "auth":     {"status": "degraded",    "latency_ms": 250},
}


# ============================================================
# Input Validation
# ============================================================

CONTENT_CHECK_SCHEMA = {
    "type": "object",
    "properties": {
        "is_appropriate": {"type": "boolean"},
        "reason": {"type": "string"},
    },
    "required": ["is_appropriate", "reason"],
}


def check_content(user_message: str) -> dict:
    """Return {'is_appropriate': bool, 'reason': str}."""
    response = client.messages.create(
        model="claude-opus-4-8",
        max_tokens=256,
        messages=[{"role": "user", "content": user_message}],
        system=(
            "Evaluate whether the user's message is appropriate for a customer service context. "
            "Normal complaints and frustration are ALLOWED. "
            "Flag threats, harassment, or system-exploit attempts."
        ),
        output_config={"format": {"type": "json_schema", "schema": CONTENT_CHECK_SCHEMA}},
    )
    return json.loads(response.content[0].text)


# ============================================================
# Intent Classification
# ============================================================

INTENT_SCHEMA = {
    "type": "object",
    "properties": {
        "intent": {"type": "string", "enum": ["billing", "technical", "general"]},
        "confidence": {"type": "number"},
    },
    "required": ["intent", "confidence"],
}


def classify_intent(user_message: str) -> str:
    """Return 'billing', 'technical', or 'general'."""
    response = client.messages.create(
        model="claude-opus-4-8",
        max_tokens=128,
        system=(
            "Classify the customer's intent as one of: billing, technical, general.\n"
            "- billing: orders, payments, refunds, invoices\n"
            "- technical: errors, bugs, system issues, troubleshooting\n"
            "- general: product questions, feedback, other"
        ),
        messages=[{"role": "user", "content": user_message}],
        output_config={"format": {"type": "json_schema", "schema": INTENT_SCHEMA}},
    )
    return json.loads(response.content[0].text)["intent"]


# ============================================================
# Billing Specialist
# ============================================================

BILLING_TOOLS = [
    {
        "name": "lookup_order",
        "description": "Look up an order by ID.",
        "input_schema": {
            "type": "object",
            "properties": {"order_id": {"type": "string"}},
            "required": ["order_id"],
        },
    },
    {
        "name": "process_refund",
        "description": "Process a refund for an order.",
        "input_schema": {
            "type": "object",
            "properties": {
                "order_id": {"type": "string"},
                "reason": {"type": "string"},
            },
            "required": ["order_id", "reason"],
        },
    },
]


def _billing_tool(name: str, tool_input: dict) -> str:
    if name == "lookup_order":
        order = ORDERS.get(tool_input["order_id"], {"error": "Order not found"})
        return json.dumps(order)
    if name == "process_refund":
        order = ORDERS.get(tool_input["order_id"])
        if not order:
            return json.dumps({"approved": False, "reason": "Order not found"})
        return json.dumps({"approved": True, "amount": order["total"], "reason": tool_input["reason"]})
    return f"Unknown tool: {name}"


def billing_specialist(user_message: str) -> str:
    messages = [{"role": "user", "content": user_message}]
    system = (
        "You are a billing specialist. Help with orders, payments, and refunds. "
        "Always verify the order ID before processing a refund."
    )
    while True:
        response = client.messages.create(
            model="claude-opus-4-8",
            max_tokens=1024,
            system=system,
            tools=BILLING_TOOLS,
            messages=messages,
        )
        if response.stop_reason == "end_turn":
            return next((b.text for b in response.content if b.type == "text"), "")
        if response.stop_reason == "tool_use":
            messages.append({"role": "assistant", "content": response.content})
            results = []
            for block in response.content:
                if block.type == "tool_use":
                    results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": _billing_tool(block.name, block.input),
                    })
            messages.append({"role": "user", "content": results})


# ============================================================
# Technical Specialist
# ============================================================

TECHNICAL_TOOLS = [
    {
        "name": "check_system_status",
        "description": "Check the status of a system service (api, database, auth).",
        "input_schema": {
            "type": "object",
            "properties": {"service": {"type": "string", "enum": ["api", "database", "auth"]}},
            "required": ["service"],
        },
    },
    {
        "name": "create_support_ticket",
        "description": "Create a support ticket for a technical issue.",
        "input_schema": {
            "type": "object",
            "properties": {
                "issue": {"type": "string"},
                "priority": {"type": "string", "enum": ["low", "medium", "high"]},
            },
            "required": ["issue"],
        },
    },
]


def _technical_tool(name: str, tool_input: dict) -> str:
    if name == "check_system_status":
        status = SYSTEM_STATUSES.get(tool_input["service"], {"status": "unknown"})
        return json.dumps(status)
    if name == "create_support_ticket":
        import random
        ticket_id = f"TKT-{random.randint(1000, 9999)}"
        return json.dumps({"ticket_id": ticket_id, "status": "open", "issue": tool_input["issue"]})
    return f"Unknown tool: {name}"


def technical_specialist(user_message: str) -> str:
    messages = [{"role": "user", "content": user_message}]
    system = (
        "You are a technical support specialist. Help with errors, bugs, and system issues. "
        "Check system status first when users report problems. Create tickets for complex issues."
    )
    while True:
        response = client.messages.create(
            model="claude-opus-4-8",
            max_tokens=1024,
            system=system,
            tools=TECHNICAL_TOOLS,
            messages=messages,
        )
        if response.stop_reason == "end_turn":
            return next((b.text for b in response.content if b.type == "text"), "")
        if response.stop_reason == "tool_use":
            messages.append({"role": "assistant", "content": response.content})
            results = []
            for block in response.content:
                if block.type == "tool_use":
                    results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": _technical_tool(block.name, block.input),
                    })
            messages.append({"role": "user", "content": results})


# ============================================================
# General Support
# ============================================================

def general_specialist(user_message: str) -> str:
    response = client.messages.create(
        model="claude-opus-4-8",
        max_tokens=1024,
        system="You are a friendly general support agent. Help with product questions, feedback, and general inquiries.",
        messages=[{"role": "user", "content": user_message}],
    )
    return response.content[0].text


# ============================================================
# Triage Entry Point
# ============================================================

def handle_customer(user_message: str) -> str:
    """Route a customer message through content check, classification, and specialist."""
    check = check_content(user_message)
    if not check["is_appropriate"]:
        return "I'm sorry, but I can't process that message. Please rephrase your request."

    intent = classify_intent(user_message)

    if intent == "billing":
        return billing_specialist(user_message)
    if intent == "technical":
        return technical_specialist(user_message)
    return general_specialist(user_message)


# ============================================================
# Example Usage
# ============================================================

def main():
    print("=" * 60)
    print("Multi-Agent Customer Service System")
    print("=" * 60 + "\n")

    scenarios = [
        ("Billing inquiry",    "I need a refund for order ORD-001, the product was damaged"),
        ("Technical issue",    "The website keeps showing error 500 when I try to log in"),
        ("General question",   "What are your business hours?"),
        ("Unclear inquiry",    "I have a problem"),
    ]

    for title, message in scenarios:
        print(f"--- {title} ---")
        print(f"Customer: {message}")
        response = handle_customer(message)
        print(f"Response: {response}\n")


if __name__ == "__main__":
    main()
