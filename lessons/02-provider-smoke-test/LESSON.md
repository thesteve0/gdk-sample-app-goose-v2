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
  local-lamacpp-glimmer.json
  src/
    gdk_hello/
      __init__.py
      main.py
  lessons/
```

Only `src/` code is snapshotted per lesson for reference. Configuration files, the virtual environment, and provider JSON configs remain at repo root.

## Prerequisites
- Lesson 1 complete: `pyproject.toml`, `.env.example`, `.gitignore` at repo root, `src/gdk_hello`
- `uv venv` exists at repo root and `goose-sdk` is installed from source
- llama.cpp server running and exposing OpenAI-compatible API

### Provider config files
- `local-lamacpp-glimmer.json` lives at repo root. It is a declarative provider config for an OpenAI-compatible llama.cpp endpoint.
- JSON fields map to `.env` values:
  - `base_url` in JSON → should match `OPENAI_BASE_URL` in `.env`
  - `api_key_env` in JSON → name of env var, typically `OPENAI_API_KEY` in `.env`
  - Model name is not stored in JSON; use `MODEL_NAME` from `.env` when building `ProviderModelConfig`.

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
- `OPENAI_BASE_URL` → Used for reference and for building declarative configs. The declarative JSON `base_url` is used for all requests; `openai_provider` factory is hard-coded to `https://api.openai.com`.
- `OPENAI_API_KEY` → Required by the provider even for local servers. Dummy is fine; declarative config can set `requires_auth: false`.
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
- `declarative_provider_from_json(json: str) -> Provider` — factory for providers defined via JSON config. Supports `engine: "openai"` with `base_url`, `api_key_env`, etc. Used for OpenAI-compatible local servers.
- `openai_provider(api_key: str) -> Provider` — factory for OpenAI cloud provider. Hard-coded to `https://api.openai.com`, does not accept a URL.
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

For OpenAI-compatible local servers the UniFFI `openai_provider` factory is hard-coded to `https://api.openai.com`. Base URL is **not** configurable via that factory. Use the declarative constructor for local llama.cpp.

Repo root file:
`local-lamacpp-glimmer.json`

Reference the official example for exact signatures:
- Example: https://github.com/aaif-goose/goose/blob/main/crates/goose-sdk/examples/uniffi/provider.py
- API reference and source of truth:
  - `declarative_provider_from_json(json: str) -> Provider` – source `crates/goose-sdk/src/bindings.rs` `declarative_provider_from_json` and docs https://goose-docs.ai/docs/gdk/sdk/api-reference?version=0.1&language=python#fn-declarative-provider-from-json
  - `ProviderModelConfig` – source `crates/goose-sdk/src/bindings.rs` `ProviderModelConfig` and docs https://goose-docs.ai/docs/gdk/sdk/api-reference?version=0.1&language=python#providermodelconfig
  - `ProviderMessage` / `MessageRole` / `MessageContent` – source `crates/goose-sdk/src/bindings.rs` and docs https://goose-docs.ai/docs/gdk/sdk/api-reference?version=0.1&language=python#providermessage
  - `Provider.stream(model, system, messages, tools) -> ProviderStream` – docs https://goose-docs.ai/docs/gdk/sdk/api-reference?version=0.1&language=python#providerstream
  - `ProviderStream.next_chunk() -> Optional[StreamChunk]` – docs https://goose-docs.ai/docs/gdk/sdk/api-reference?version=0.1&language=python#providerstream
  - Generated API data: `documentation/src/data/gdk-api.json` via `documentation/automation/gdk-api/generate.py`

Note: `openai_provider` does NOT accept a URL and is hard-coded to `https://api.openai.com`. For OpenAI-compatible endpoints use `declarative_provider_from_json` with a JSON config that specifies `engine: "openai"` and `base_url`. `ProviderModelConfig` is for model parameters only, not connection parameters.

Steps to implement:
1. Load environment variables with `python-dotenv`.
2. Import `declarative_provider_from_json`, `ProviderModelConfig`, `ProviderMessage`, `MessageRole`, `MessageContent` from `goose`.
3. Load the declarative config:
   - `with open("local-lamacpp-glimmer.json") as f: provider_json = f.read()`
   - `provider = declarative_provider_from_json(provider_json)`
4. Build config:
   - Read `MODEL_NAME` from env for verification. Base URL and auth come from the JSON file.
   - Create `ProviderModelConfig(model_name=MODEL_NAME)`
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
