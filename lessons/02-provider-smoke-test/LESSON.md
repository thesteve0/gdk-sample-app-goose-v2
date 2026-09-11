# Lesson 2: Provider Smoke Test

## Goal
Verify that the Goose Development Kit can connect to your OpenAI-compatible llama.cpp endpoint and produce streaming output. This lesson validates provider instantiation, message construction, and chunk iteration end-to-end.

## Context
This lesson builds directly on Lesson 1 bootstrap. We keep the same `src/gdk_hello` layout and shared venv at repo root. A snapshot copy of the working code is kept in `02-provider-smoke-test/` for reference; configuration files, `.venv`, and the provider JSON remain at repo root.

## Directory structure

Snapshot (reference):
```
02-provider-smoke-test/
  __init__.py     - package marker
  main.py         - working smoke test implementation
```

Repo root (shared across all lessons):
```
gdk-sample-app-goose-build-v2/
  pyproject.toml                  # package config, goose-sdk==0.1.0a8
  .env.example                    # template for local server env vars
  .env                            # your actual env (gitignored)
  .gitignore                      # excludes .env, __pycache__, .venv
  custom_aa_llama_qwen3_6-35b.json   # declarative provider config
  src/
    gdk_hello/
      __init__.py
      main.py                     # active source (mirrors snapshot)
  lessons/
```

Only `02-provider-smoke-test/` code is snapshotted for reference. Configuration files and the virtual environment live at repo root and are shared across all lessons.

## Prerequisites
- Lesson 1 complete: venv created with `uv venv`, packages installed
- `goose-sdk` installed (from PyPI: `goose-sdk==0.1.0a8`)
- llama.cpp server running at your configured base URL

### Provider config file
`custom_aa_llama_qwen3_6-35b.json` at repo root is a declarative provider config for an OpenAI-compatible llama.cpp endpoint. Key fields:

| JSON field | Purpose |
|---|---|
| `base_url` | Local server URL (e.g. `http://127.0.0.1:8080`) — NOT `.env.example`'s `/v1` suffix, the server handles that path |
| `api_key_env` | Empty string here; `requires_auth: false` means no key needed for local server |
| `supports_streaming` | `true` — this endpoint supports streaming responses |
| `requires_auth` | `false` — no authentication token required for local use |
| `models[0].name` | The model identifier used by llama.cpp |

### Environment variables
`.env.example` at repo root:
```
OPENAI_BASE_URL=http://127.0.0.1:8080/v1
OPENAI_API_KEY=sk-local-test
MODEL_NAME=bartowski/Muse-Glimmer-30B-GGUF:Q8_0
```

Create `.env` from the example and adjust values to match your llama.cpp setup:
```bash
cp .env.example .env
```

Edit `.env`:
- `OPENAI_BASE_URL` — matches your llama.cpp base URL (must include `/v1` for OpenAI-compatible endpoints)
- `OPENAI_API_KEY` — dummy value is fine; the JSON config has `requires_auth: false`
- `MODEL_NAME` — must match what llama.cpp exposes. Verify with:
  ```bash
  curl http://127.0.0.1:8080/v1/models
  ```

Load env in Python via `python-dotenv`:
```python
from dotenv import load_dotenv
load_dotenv()  # loads .env from cwd (repo root)
```

## Step 2.1: Import the right types

```python
import asyncio
import os
import sys
from dotenv import load_dotenv
from goose import declarative_provider_from_json, MessageContent, StreamChunk
from goose import (
    ProviderModelConfig,
    ProviderMessage,
    ProviderStream,
    MessageRole,
)
from pathlib import Path
```

Key types:

| Type | Purpose |
|---|---|
| `declarative_provider_from_json(json)` | Factory from JSON config; supports `engine: "openai"` with `base_url` for local servers. The `openai_provider()` factory is hard-coded to `https://api.openai.com` and won't work for local endpoints. |
| `ProviderModelConfig(model_name)` | Model configuration — name only, plus optional params like `context_limit`, `temperature`, `max_tokens` |
| `ProviderMessage(role, content)` | Carries a role + list of content items to the provider |
| `MessageRole.USER` / `.ASSISTANT` / `.TOOL` | Message roles (enum) |
| `MessageContent.TEXT(text=...)` | Plain text message content (enum variant — construct with `.TEXT()`) |
| `ProviderStream` | Async iterable stream of response chunks |
| `StreamChunk.TEXT_CHUNK` / `.END_CHUNK` / `.ERROR_CHUNK` | Chunk type classes, used with `isinstance()` |

References:
- SDK source: https://github.com/aaif-goose/goose/blob/main/crates/goose-sdk/src/bindings.rs
- Python example: https://github.com/aaif-goose/goose/blob/main/crates/goose-sdk/examples/uniffi/provider.py
- `ProviderMessage` / `MessageRole` / `MessageContent`: enum definitions in [bindings.rs](https://github.com/aaif-goose/goose/blob/main/crates/goose-sdk/src/bindings.rs) (lines 191–237)
- `StreamChunk`: variant definitions in [bindings.rs](https://github.com/aaif-goose/goose/blob/main/crates/goose-sdk/src/bindings.rs) (lines 554–580)

## Step 2.2: Smoke test code

The snapshot at `02-provider-smoke-test/main.py` contains the complete implementation. Read it to understand the flow, then write your own version in `src/gdk_hello/main.py`.

```python
import asyncio
import os
import sys
from dotenv import load_dotenv
from goose import declarative_provider_from_json, MessageContent, StreamChunk
from goose import (
    ProviderModelConfig,
    ProviderMessage,
    ProviderStream,
    MessageRole,
)
from pathlib import Path


async def main() -> None:
    load_dotenv()
    if not Path("custom_aa_llama_qwen3_6-35b.json").exists():
        raise FileNotFoundError(
            "Run from repo root with `python -m src.gdk_hello.main`"
        )

    # 1. Load declarative provider config
    provider = declarative_provider_from_json(
        Path("custom_aa_llama_qwen3_6-35b.json").read_text()
    )

    # 2. Build model config (model name from .env)
    model = ProviderModelConfig(model_name=os.getenv("MODEL_NAME"))

    # 3. Build user message list
    messages = [
        ProviderMessage(
            role=MessageRole.USER,
            content=[MessageContent.TEXT(
                text="Should I build a Goose SDK application with Rust or with Python?"
            )],
        )
    ]

    # 4. Stream the response
    stream = await provider.stream(
        model=model,
        system="you are an expert on the goose SDK",
        messages=messages,
        tools=[],
    )
    print("Streaming response...", file=sys.stderr)

    try:
        while chunk := await stream.next_chunk():
            if isinstance(chunk, StreamChunk.TEXT_CHUNK):
                print(chunk.text, end="", flush=True)
            elif isinstance(chunk, StreamChunk.END_CHUNK) and getattr(
                chunk, "usage", None
            ):
                print(f"\n\nusage: {chunk.usage}", file=sys.stderr)
            elif isinstance(chunk, StreamChunk.ERROR_CHUNK):
                print(
                    f"\n\nerror: {chunk.error.message}", file=sys.stderr
                )
    except Exception as e:
        print(f"\n\nError during streaming: {e}", file=sys.stderr)
        raise
    print()


if __name__ == "__main__":
    asyncio.run(main())
```

### How the smoke test works

1. **`load_dotenv()`** — loads `.env` from cwd (repo root) so `MODEL_NAME` is available via `os.getenv`
2. **`declarative_provider_from_json(...)`** — reads the JSON config and returns a configured provider. This validates that:
   - The JSON is valid
   - The engine type (`openai`) is recognized
   - All required fields parse correctly
3. **`ProviderModelConfig(model_name=...)`** — wraps the model name (and optionally context limit, temperature, max tokens). Base URL and auth come from the JSON config, not this object.
4. **`ProviderMessage(role=..., content=[...])`** — builds a user message with text content
5. **`provider.stream(model, system, messages, tools)`** — async call that returns a `ProviderStream`
6. **Chunk loop** — iterates async chunks:
   - `TEXT_CHUNK`: model's text output — print immediately (end="", flush=True)
   - `END_CHUNK`: stream complete — print usage stats to stderr if available
   - `ERROR_CHUNK`: provider error — print error message to stderr

### Chunk types reference

| Variant | Attribute | When it arrives |
|---|---|---|
| `StreamChunk.TEXT_CHUNK` | `.text: str` | Each turn during generation |
| `StreamChunk.END_CHUNK` | `.usage: Optional[Usage]` | Once at stream end |
| `StreamChunk.ERROR_CHUNK` | `.error.message: str` | If the provider encounters an error |

## Step 2.3: Run the smoke test

From repo root:
```bash
uv run python -m src.gdk_hello.main
```

**Expected output:**
- stderr (in `[2m` brackets): `Streaming response...`
- stdout: The model's reply streaming line by line
- stderr (at end): `usage:` with token counts and model name

If the server is unreachable, you'll see an error message. If the config is wrong, `declarative_provider_from_json()` will raise before any streaming begins.

### Success criteria
- No import errors
- Config loads without exception
- Streaming output appears (text chunks) or a clear network error
- Usage stats printed at end (if server returns them)

## Best practices

- Always run from repo root so `Path("custom_aa_llama_qwen3_6-35b.json")` resolves correctly
- Use `python -m src.gdk_hello.main` rather than a direct file path — the `src/` layout requires the package import system
- Print streaming text to stdout, diagnostics (usage, errors) to stderr
- Wrap chunk iteration in try/except — network errors during streaming are common during development
- The `tools=[]` argument is required by `stream()`; an empty list means no tool support (Lesson 5 covers tools)

## Next steps
Once smoke test passes:
- Lesson 3: Deepen streaming knowledge — understand chunk types, usage parsing, and error handling patterns.
- Lesson 4: System prompt and message roles — multi-turn conversation with assistant responses
- Lesson 5: Add first `ProviderTool` definition — enable the model to call custom functions

## Questions to ask before proceeding
- What is your exact llama.cpp base URL and model name?
- Does streaming output appear when you run the script?
- Are usage stats printed at the end?