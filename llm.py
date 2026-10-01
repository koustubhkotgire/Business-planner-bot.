"""Thin wrapper around any OpenAI-compatible FREE provider (Groq by default)."""
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

GROQ_MODEL = os.getenv("LLM_MODEL", "openai/gpt-oss-120b")
GROQ_URL = os.getenv("LLM_BASE_URL", "https://api.groq.com/openai/v1")

# name -> (base_url, default_model). Free-tier limits change; check provider docs.
PROVIDERS = {
    "Groq (free)": (GROQ_URL, GROQ_MODEL),
    "Google Gemini (free)": ("https://generativelanguage.googleapis.com/v1beta/openai/", "gemini-2.0-flash"),
    "OpenRouter (free models)": ("https://openrouter.ai/api/v1", "meta-llama/llama-3.3-70b-instruct:free"),
    "Ollama (local, free)": ("http://localhost:11434/v1", "llama3.1"),
}

# Reads LLM_API_KEY from .env (falls back to GROQ_API_KEY if you use that name)
DEFAULT_KEY = os.getenv("LLM_API_KEY") or os.getenv("GROQ_API_KEY", "")


def get_client(base_url: str, api_key: str) -> OpenAI:
    return OpenAI(base_url=base_url, api_key=api_key or "ollama")


def stream_chat(client, model, messages, temperature=0.6):
    """Yield text chunks. Errors are yielded as text so the UI never crashes."""
    try:
        stream = client.chat.completions.create(
            model=model, messages=messages, stream=True, temperature=temperature
        )
        for chunk in stream:
            if chunk.choices and chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
    except Exception as e:
        yield f"\n\n⚠️ Model error: {e}"


def complete(client, model, messages, temperature=0.2) -> str:
    resp = client.chat.completions.create(
        model=model, messages=messages, temperature=temperature
    )
    return resp.choices[0].message.content or ""