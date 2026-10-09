# CuriousScan Free-Model Router

One key, many free models. Send a prompt to the free tiers of several LLM
providers through a single CLI — with automatic fallback when a model is
busy, rate-limited, or down.

## Setup (one time)

1. Get a free API key at **https://openrouter.ai/keys** (no card required).
2. Export it:

```bash
export OPENROUTER_API_KEY="sk-or-..."
```

## Usage

```bash
# ask the default model chain (falls back automatically)
python router.py "Explain recursion like I'm five"

# prefer a specific model, fall back to the rest on failure
python router.py "Write a haiku about GPUs" --model google/gemma-3-27b-it:free

# pipe input, add a system prompt
echo "Summarize: ..." | python router.py --system "You are a terse assistant."

# see the configured free-tier lineup
python router.py --list-models

# benchmark the free-tier answer against Claude, side by side
export ANTHROPIC_API_KEY="sk-ant-..."
python router.py "Explain recursion like I'm five" --claude-benchmark
```

## Claude benchmark (optional)

Free tiers are great — but how good are they, really? `--claude-benchmark`
answers your prompt twice: once through the free-tier chain, once through
Claude (Sonnet), printed side by side. Claude is the quality bar the free
answers are judged against. Needs an Anthropic API key; still stdlib only,
no SDK required. `--claude-model` overrides the default (`claude-sonnet-5-5`).

## How it works

- Talks to OpenRouter's unified chat API (`/api/v1/chat/completions`)
- Tries your preferred model first, then walks the fallback table
- A model that errors (429/404/5xx) is skipped, not fatal
- Sends `HTTP-Referer: https://curiousscan.in` so free-tier usage is attributed

## Notes

- Free-tier lineups rotate — check https://openrouter.ai/models and edit the
  `MODELS` table in `router.py` when a model disappears.
- Unauthenticated GitHub-style rate limits don't apply here; OpenRouter
  free models have their own per-day caps.

## Requirements

Python 3.8+. Stdlib only — zero dependencies.

## License

MIT — see `LICENSE`.

---
Built by [CuriousScan](https://curiousscan.in) — *Less noise. More signal.*
