from typing import Any

from litellm import completion

MODEL_FALLBACKS = [
    "gpt-4o-mini", 
    "gpt-4o", 
    "claude-3.5", 
    "gemini-pro", 
    "groq-1.0", 
]

PROVIDER_MODEL_MAP = {
    "openai": ["gpt-4o-mini", "gpt-4o"],
    "anthropic": ["claude-3.5", "claude-3"],
    "gemini": ["gemini-pro", "gemini-1.0"],
    "groq": ["groq-1.0"],
    "deepseek": ["deepseek-v1"],
}

DEFAULT_TOOL_FUNCTIONS = [
    {
        "name": "navigate_url",
        "description": "Navigate browser to a URL.",
        "parameters": {
            "type": "object",
            "properties": {
                "url": {"type": "string", "description": "Target URL."}
            },
            "required": ["url"],
        },
    },
    {
        "name": "click_element",
        "description": "Click an element on the page by selector.",
        "parameters": {
            "type": "object",
            "properties": {
                "selector": {"type": "string", "description": "CSS or XPath selector."}
            },
            "required": ["selector"],
        },
    },
    {
        "name": "type_text",
        "description": "Type text into an input field by selector.",
        "parameters": {
            "type": "object",
            "properties": {
                "selector": {"type": "string"},
                "text": {"type": "string"},
            },
            "required": ["selector", "text"],
        },
    },
    {
        "name": "extract_text",
        "description": "Extract visible text from the current page.",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    },
    {
        "name": "task_complete",
        "description": "Mark the task as complete with the final result.",
        "parameters": {
            "type": "object",
            "properties": {
                "result": {"type": "string"}
            },
            "required": ["result"],
        },
    },
]


def choose_model(api_key: str, provider: str | None = None) -> str:
    if provider and provider in PROVIDER_MODEL_MAP:
        return PROVIDER_MODEL_MAP[provider][0]
    return MODEL_FALLBACKS[0]


def call_llm(prompt: str, tool_messages: list[dict[str, Any]] | None = None, api_key: str | None = None, provider: str | None = None) -> Any:
    model = choose_model(api_key=api_key or "", provider=provider)
    params = {
        "model": model,
        "messages": tool_messages or [{"role": "system", "content": prompt}],
        "temperature": 0.2,
        "max_tokens": 800,
        "function_call": "auto",
        "functions": DEFAULT_TOOL_FUNCTIONS,
    }
    if api_key:
        params["api_key"] = api_key
    return completion(**params)
