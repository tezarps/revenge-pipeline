"""Shared LLM utility — Anthropic API (Sonnet 5 for stories, Haiku for short jobs)."""
import sys
from pathlib import Path

import anthropic

sys.path.insert(0, str(Path(__file__).parent.parent))
from config import ANTHROPIC_API_KEY, SONNET_MODEL, HAIKU_MODEL

_client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)


def call(user, system="", max_tokens=16000, model=None):
    """Streaming call — required for long story outputs (>10K tokens) to
    avoid HTTP timeouts."""
    kwargs = dict(
        model=model or SONNET_MODEL,
        max_tokens=max_tokens,
        messages=[{"role": "user", "content": user}],
    )
    if system:
        kwargs["system"] = system
    with _client.messages.stream(**kwargs) as stream:
        msg = stream.get_final_message()
    return "".join(b.text for b in msg.content if b.type == "text").strip()


def call_haiku(user, system="", max_tokens=2000):
    return call(user, system=system, max_tokens=max_tokens, model=HAIKU_MODEL)
