"""
Basic Agent Example

Demonstrates the fundamental setup and usage of the Anthropic SDK:
- Simple text responses
- Tool use loop
- Multi-turn conversation
- Structured output via JSON schema
"""

import json
from anthropic import Anthropic

client = Anthropic()


# ============================================================
# Tool Definitions
# ============================================================

TOOLS = [
    {
        "name": "get_current_time",
        "description": "Get the current date and time.",
        "input_schema": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    },
    {
        "name": "calculate",
        "description": "Safely evaluate a mathematical expression like '2 + 2' or '10 * 5'.",
        "input_schema": {
            "type": "object",
            "properties": {
                "expression": {
                    "type": "string",
                    "description": "A mathematical expression using +, -, *, /, (, ).",
                },
            },
            "required": ["expression"],
        },
    },
]


def _run_tool(name: str, tool_input: dict) -> str:
    if name == "get_current_time":
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if name == "calculate":
        expression = tool_input["expression"]
        allowed = set("0123456789+-*/.() ")
        if not all(c in allowed for c in expression):
            return "Error: invalid characters in expression"
        try:
            return str(eval(expression))
        except Exception as e:
            return f"Error: {e}"

    return f"Error: unknown tool '{name}'"


# ============================================================
# Core Agent Loop
# ============================================================

def run_agent(user_message: str, system: str | None = None) -> str:
    """Run a single-turn agent with tool use, returning the final text reply."""
    messages = [{"role": "user", "content": user_message}]
    kwargs = {
        "model": "claude-opus-4-8",
        "max_tokens": 1024,
        "tools": TOOLS,
        "messages": messages,
    }
    if system:
        kwargs["system"] = system

    while True:
        response = client.messages.create(**kwargs)

        if response.stop_reason == "end_turn":
            for block in response.content:
                if block.type == "text":
                    return block.text
            return ""

        if response.stop_reason == "tool_use":
            messages.append({"role": "assistant", "content": response.content})
            tool_results = []
            for block in response.content:
                if block.type == "tool_use":
                    result = _run_tool(block.name, block.input)
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": result,
                    })
            messages.append({"role": "user", "content": tool_results})
            kwargs["messages"] = messages


# ============================================================
# Multi-Turn Conversation
# ============================================================

class ConversationAgent:
    """Stateful multi-turn conversation with tool support."""

    def __init__(self, system: str):
        self.system = system
        self.messages: list[dict] = []

    def chat(self, user_message: str) -> str:
        self.messages.append({"role": "user", "content": user_message})

        while True:
            response = client.messages.create(
                model="claude-opus-4-8",
                max_tokens=1024,
                system=self.system,
                tools=TOOLS,
                messages=self.messages,
            )

            if response.stop_reason == "end_turn":
                text = next(
                    (b.text for b in response.content if b.type == "text"), ""
                )
                self.messages.append({"role": "assistant", "content": text})
                return text

            if response.stop_reason == "tool_use":
                self.messages.append({"role": "assistant", "content": response.content})
                tool_results = []
                for block in response.content:
                    if block.type == "tool_use":
                        result = _run_tool(block.name, block.input)
                        tool_results.append({
                            "type": "tool_result",
                            "tool_use_id": block.id,
                            "content": result,
                        })
                self.messages.append({"role": "user", "content": tool_results})


# ============================================================
# Structured Output
# ============================================================

TASK_RESPONSE_SCHEMA = {
    "type": "object",
    "properties": {
        "answer": {"type": "string"},
        "confidence": {"type": "number", "minimum": 0, "maximum": 1},
        "sources": {"type": "array", "items": {"type": "string"}},
    },
    "required": ["answer", "confidence", "sources"],
}


def run_structured(user_message: str) -> dict:
    """Return a structured JSON response validated against a schema."""
    response = client.messages.create(
        model="claude-opus-4-8",
        max_tokens=1024,
        messages=[{"role": "user", "content": user_message}],
        output_config={"format": {"type": "json_schema", "schema": TASK_RESPONSE_SCHEMA}},
    )
    return json.loads(response.content[0].text)


# ============================================================
# Examples
# ============================================================

def basic_example():
    print("=== Basic Agent Example ===\n")

    print(run_agent("What time is it?"))
    print()
    print(run_agent("Calculate 15 * 7 + 23"))
    print()
    print(run_agent("What is the capital of Japan?"))
    print()


def multi_turn_example():
    print("=== Multi-Turn Conversation ===\n")

    agent = ConversationAgent(system="You are a helpful assistant. Be concise.")
    print(agent.chat("My name is Alice."))
    print(agent.chat("What's my name?"))
    print(agent.chat("Calculate the square of 12."))
    print()


def structured_example():
    print("=== Structured Output ===\n")

    result = run_structured("What is machine learning?")
    print(f"Answer:     {result['answer'][:80]}...")
    print(f"Confidence: {result['confidence']}")
    print(f"Sources:    {result['sources']}")
    print()


def main():
    basic_example()
    multi_turn_example()
    structured_example()


if __name__ == "__main__":
    main()
