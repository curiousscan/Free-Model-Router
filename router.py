#!/usr/bin/env python3
"""
CuriousScan Free-Model Router
=============================
One key, many free models. Point a single prompt at the free tiers of several
LLM providers and get an answer back — with automatic fallback when a model
is busy or rate-limited.

Needs one free API key: https://openrouter.ai/keys (no card required).
Export it first:

    export OPENROUTER_API_KEY="sk-or-..."

Usage:
    python router.py "Explain recursion like I'm five"
    python router.py "Write a haiku about GPUs" --model google/gemma-3-27b-it:free
    python router.py --list-models
    echo "Summarize this" | python router.py --system "You are a terse assistant."

Stdlib only — no dependencies.
"""

import argparse
import json
import os
import sys
import urllib.request
import urllib.error

VERSION = "0.1.0"
API_URL = "https://openrouter.ai/api/v1/chat/completions"

# Free-tier lineup. Providers rotate free models regularly — verify the current
# list at https://openrouter.ai/models and edit this table as needed.
MODELS = [
    ("meta-llama/llama-3.3-70b-instruct:free", "Meta Llama 3.3 70B — strong all-rounder"),
    ("qwen/qwen-2.5-72b-instruct:free", "Qwen 2.5 72B — strong all-rounder"),
    ("google/gemma-3-27b-it:free", "Google Gemma 3 27B — fast, capable"),
    ("deepseek/deepseek-chat-v3-0324:free", "DeepSeek V3 — reasoning-heavy tasks"),
    ("mistralai/mistral-small-3.1-24b-instruct:free", "Mistral Small 3.1 — quick answers"),
]


def get_key():
    key = os.environ.get("OPENROUTER_API_KEY", "").strip()
    if not key:
        print(
            "ERROR: OPENROUTER_API_KEY is not set.\n"
            "Get a free key (no card required) at https://openrouter.ai/keys\n"
            "then run: export OPENROUTER_API_KEY=\"sk-or-...\"",
            file=sys.stderr,
        )
        sys.exit(2)
    return key


def chat(model, messages, max_tokens, key):
    payload = json.dumps(
        {"model": model, "messages": messages, "max_tokens": max_tokens}
    ).encode()
    req = urllib.request.Request(
        API_URL,
        data=payload,
        headers={
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://curiousscan.in",
            "X-Title": "CuriousScan Free-Model Router",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = json.load(resp)
        return data["choices"][0]["message"]["content"]
    except urllib.error.HTTPError as exc:
        body = exc.read().decode(errors="replace")[:300]
        raise RuntimeError(f"{model} -> HTTP {exc.code}: {body}")
    except (KeyError, IndexError):
        raise RuntimeError(f"{model} -> unexpected response shape")


def main():
    ap = argparse.ArgumentParser(
        description="Route one prompt across free LLM tiers with automatic fallback."
    )
    ap.add_argument("prompt", nargs="?", help="The prompt. If omitted, read from stdin.")
    ap.add_argument("--model", default=None,
                    help="Preferred model id. Others are tried as fallback.")
    ap.add_argument("--system", default=None, help="System prompt.")
    ap.add_argument("--max-tokens", type=int, default=1024)
    ap.add_argument("--list-models", action="store_true", help="Show the model table and exit.")
    args = ap.parse_args()

    if args.list_models:
        for mid, note in MODELS:
            print(f"{mid}\n  {note}\n")
        return

    prompt = args.prompt
    if not prompt:
        if sys.stdin.isatty():
            ap.error("give a prompt argument or pipe one via stdin")
        prompt = sys.stdin.read().strip()
    if not prompt:
        ap.error("empty prompt")

    key = get_key()
    messages = []
    if args.system:
        messages.append({"role": "system", "content": args.system})
    messages.append({"role": "user", "content": prompt})

    order = [m for m, _ in MODELS]
    if args.model:
        order = [args.model] + [m for m in order if m != args.model]

    errors = []
    for model in order:
        try:
            print(chat(model, messages, args.max_tokens, key))
            return
        except RuntimeError as exc:
            print(f"[!] {exc}", file=sys.stderr)
            errors.append(str(exc))
    print(f"\nAll {len(order)} models failed.", file=sys.stderr)
    sys.exit(1)


if __name__ == "__main__":
    main()
