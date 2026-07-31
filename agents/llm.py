"""Shared LLM utility. DeepSeek only (user decision 2026-07-07: moved
premise/metadata generation off Anthropic Haiku too, after a run failed
on an empty Anthropic credit balance, no reason to depend on two billing
accounts when DeepSeek already covers the long-form script)."""
import http.client
import json
import socket
import time
import urllib.error
import urllib.request

from config import DEEPSEEK_API_KEY, DEEPSEEK_MODEL

# Errors seen from long chunked-transfer reads getting cut mid-stream
# (run #127, 2026-07-31: IncompleteRead(1 bytes read) ~65s into a script
# call, nothing wrong with the request, just the connection dying before
# the final chunk boundary). None of these mean the request was bad, so
# retrying the same call is the right move rather than surfacing to the
# pipeline as a hard failure.
_TRANSIENT_ERRORS = (http.client.IncompleteRead, ConnectionError, socket.timeout, urllib.error.URLError)


def call_deepseek(user, system="", max_tokens=32000, timeout=300, retries=3):
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

    last_error = None
    for attempt in range(1, retries + 1):
        req = urllib.request.Request(
            "https://api.deepseek.com/chat/completions",
            data=body,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
            },
        )
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                data = json.loads(resp.read())
            return data["choices"][0]["message"]["content"].strip()
        except _TRANSIENT_ERRORS as e:
            last_error = e
            if attempt < retries:
                print(f"    DeepSeek connection dropped ({e!r}), retrying ({attempt}/{retries})...")
                time.sleep(5 * attempt)
    raise RuntimeError(f"DeepSeek connection kept failing after {retries} attempts: {last_error!r}")
