"""Shared LLM utility, Anthropic API (Haiku for short jobs) plus DeepSeek
(the long-form story script, see call_deepseek)."""
import json
import sys
import urllib.request
from pathlib import Path

import anthropic

sys.path.insert(0, str(Path(__file__).parent.parent))
from config import ANTHROPIC_API_KEY, DEEPSEEK_API_KEY, SONNET_MODEL, HAIKU_MODEL, DEEPSEEK_MODEL

_client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)


def call(user, system="", max_tokens=16000, model=None):
    """Streaming call, required for long story outputs (>10K tokens) to
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


def call_deepseek(user, system="", max_tokens=32000, timeout=300):
    """DeepSeek's top tier (deepseek-v4-pro), used for the long-form story
    script in place of Sonnet (user decision 2026-07-06, own API key, to
    cut the ~$1.25/video script cost to near zero). This is a REASONING
    model: it spends some of max_tokens on a hidden reasoning pass before
    the actual output, so max_tokens must stay generous (32K default) or
    a long script can get truncated with nothing but reasoning tokens
    spent and no visible content (seen directly during a max_tokens=10
    smoke test). Plain urllib, OpenAI-compatible REST endpoint, no new
    pip dependency, same pattern as apophenia-pipeline's DeepSeek calls."""
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": user})
    body = json.dumps({
        "model": DEEPSEEK_MODEL,
        "messages": messages,
        "max_tokens": max_tokens,
    }).encode()
    req = urllib.request.Request(
        "https://api.deepseek.com/chat/completions",
        data=body,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        },
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        data = json.loads(resp.read())
    return data["choices"][0]["message"]["content"].strip()
