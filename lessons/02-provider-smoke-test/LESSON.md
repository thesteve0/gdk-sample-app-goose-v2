# Lesson 2: Minimal Provider Smoke Test

## Goal
Verify that the Goose Development Kit can connect to your OpenAI-compatible llama.cpp endpoint and instantiate a Provider without errors. This is a configuration validation step before streaming messages.

## Context
This lesson builds directly on Lesson 1 bootstrap. We keep the same `src/gdk_hello` layout and shared venv at repo root. The lesson directory contains only a snapshot of the `src/` code for reference; `pyproject.toml`, `.venv`, `.env.example`, and `.gitignore` live at repo root and are not reproduced per lesson.

## Directory structure
```
lessons/02-provider-smoke-test/
  LESSON.md
  src/
    gdk_hello/
      __init__.py
      main.py
```

Repo root (shared across lessons):
```
gdk-sample-app-goose-build-v2/
  pyproject.toml
  .env.example
  .gitignore
  .venv/
  src/
    gdk_hello/
      __init__.py
      main.py
  lessons/
```

Only `src/` code is snapshotted per lesson for reference. Configuration files and the virtual environment remain at repo root.

## Prerequisites
- Lesson 1 complete: `pyproject.toml`, `.env.example`, `.gitignore` at repo root, `src/gdk_hello`
- `uv venv` exists at repo root and `goose-sdk` is installed from source
- llama.cpp server running and exposing OpenAI-compatible API

## Step 2.1: Environment for llama.cpp

Create `.env` at repo root from `.env.example`:
```bash
cp .env.example .env
```

Edit `.env` at repo root with your llama.cpp values:
```
OPENAI_BASE_URL=http://127.0.0.1:8080/v1
OPENAI_API_KEY=sk-local-test
MODEL_NAME=<model-name-as-exposed-by-llama.cpp>
```

Why these vars:
- `OPENAI_BASE_URL` → `openai_provider` uses this for all requests. Must end with `/v1`.
- `OPENAI_API_KEY` → Required by the provider even for local servers. Dummy is fine.
- `MODEL_NAME` → Must match the model name llama.cpp returns. Check with `curl http://127.0.0.1:8080/v1/models`.

Load env in Python with `python-dotenv`:
```python
from dotenv import load_dotenv
load_dotenv()
```

## Step 2.2: Understand GDK Provider concepts

Reference implementations and type definitions:
- SDK source: https://github.com/aaif-goose/goose/tree/main/crates/goose-sdk
- Python example: https://github.com/aaif-goose/goose/blob/main/crates/goose-sdk/examples/uniffi/provider.py
- README: https://github.com/aaif-goose/goose/blob/main/crates/goose-sdk/README.md

Key types from `goose`:
- `openai_provider(api_key: str) -> Provider` — factory for OpenAI-compatible provider. Base URL is read from `OPENAI_BASE_URL` env var by the provider implementation.
- `ProviderModelConfig(model_name: str, context_limit: Optional[int]=None, temperature: Optional[float]=None, max_tokens: Optional[int]=None, ...)` — model config
- `ProviderMessage(role: MessageRole, content: List[MessageContent])`
  - Roles: `MessageRole.USER`, `MessageRole.ASSISTANT`, `MessageRole.TOOL`
  - `MessageContent.TEXT(text=...)`, `MessageContent.IMAGE(mime_type, data)`, `MessageContent.DOCUMENT(mime_type, data, name)`
- `Provider.stream(model: ProviderModelConfig, system: str, messages: List[ProviderMessage], tools: List[ProviderTool]) -> ProviderStream`
- `ProviderStream.next_chunk() -> Optional[StreamChunk]`
  - Chunk variants: `StreamChunk.TextChunk`, `StreamChunk.EndChunk`, `StreamChunk.ErrorChunk`, ...

Smoke test does NOT need to handle streaming yet, only instantiate provider and config.

## Step 2.3: Smoke test plan

Create a small script under `src/gdk_hello/` or a temporary file for testing. Do NOT copy-paste; write it yourself.

Reference the official example for exact signatures:
- Example: https://github.com/aaif-goose/goose/blob/main/crates/goose-sdk/examples/uniffi/provider.py

Steps to implement:
1. Load environment variables.
2. Import `openai_provider`, `ProviderModelConfig`, `ProviderMessage`, `MessageRole`, `MessageContent` from `goose`.
3. Build config:
   - Read `OPENAI_API_KEY` and `MODEL_NAME` from env. `OPENAI_BASE_URL` is used by the provider via env.
   - Create `ProviderModelConfig(model_name=MODEL_NAME)`
4. Instantiate provider:
   - `provider = openai_provider(api_key=OPENAI_API_KEY)`
5. Validate:
   - Print config values to confirm they loaded.
   - Attempt to create a stream with a minimal user message, e.g. "ping".
   - Use `provider.stream(model_config, system, messages, [])` to get a `ProviderStream`.
   - Catch exceptions and print them. Success = no config error, even if server is down.

Success criteria:
- No import errors.
- Config values printed correctly.
- Provider instantiation succeeds.
- Stream creation succeeds or fails with a clear network error, not a config error.

## Step 2.4: Best practices

- Keep provider creation separate from CLI logic. Pure function `make_provider()` is ideal.
- Never hardcode secrets. Always read from env at repo root.
- Print config for debugging, but redact API key in logs.
- Use `src/` layout so imports work: `from gdk_hello import ...`
- Work from repo root; `pyproject.toml` and `.venv` are shared, not duplicated per lesson.

## Next steps
Once smoke test passes:
- Lesson 3: First streaming call – build `ProviderMessage` list, stream `TextChunk`s, print output.
- Lesson 4: System prompt and message roles.
- Lesson 5: Add first `ProviderTool` definition.

## Questions to ask before proceeding
- What is your exact llama.cpp base URL and model name?
- Do you want the smoke test script to live in `src/gdk_hello/smoke_test.py` or as a temporary `scripts/` file?
- Confirm you want to write the code yourself with guidance only.

Do not proceed to streaming until provider instantiation is verified.
