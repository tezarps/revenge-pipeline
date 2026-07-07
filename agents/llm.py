"""Shared LLM utility. DeepSeek only (user decision 2026-07-07: moved
premise/metadata generation off Anthropic Haiku too, after a run failed
on an empty Anthropic credit balance, no reason to depend on two billing
accounts when DeepSeek already covers the long-form script)."""
import json
import urllib.request

from config import DEEPSEEK_API_KEY, DEEPSEEK_MODEL


def call_deepseek(user, system="", max_tokens=32000, timeout=300):
    """DeepSeek's top tier (deepseek-v4-pro). This is a REASONING model:
    it spends some of max_tokens on a hidden reasoning pass before the
    actual output, so max_tokens must stay generous (32K default) or a
    long script can get truncated with nothing but reasoning tokens spent
    and no visible content (seen directly during a max_tokens=10 smoke
    test). Plain urllib, OpenAI-compatible REST endpoint, no new pip
    dependency, same pattern as apophenia-pipeline's DeepSeek calls."""
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
