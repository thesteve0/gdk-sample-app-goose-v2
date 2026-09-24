# Lesson 2: Provider Smoke Test

## Goal

Verify that the local OpenAI-compatible provider is reachable and that it advertises the model configured for this project.

This is intentionally only a smoke test. It does **not** construct messages, call a model completion, or process a response stream. Those concepts begin in Lesson 3.

## What this test checks

1. The declarative provider JSON can be parsed by GDK.
2. The provider's OpenAI-compatible `GET /v1/models` endpoint is reachable.
3. The endpoint returns at least one model.
4. Every model named in the provider JSON is advertised by the endpoint.

> A successful model-list request verifies server connectivity and model discovery, but it does not prove that inference works. Lesson 3 verifies inference with the first streaming call.

## Context

This lesson builds on the project created in Lesson 1. Configuration remains at the repository root, while the completed lesson code is snapshotted here:

```text
lessons/02-provider-smoke-test/
  LESSON.md
  src/
    gdk_hello/
      __init__.py
      main.py
```

The shared provider configuration remains at the repository root:

```text
custom_aa_llama_qwen3_6-35b.json
```

## Prerequisites

- Lesson 1 is complete.
- `goose-sdk==0.1.0a8` is installed.
- A compatible provider is running at the `base_url` in the provider JSON.

## Why the HTTP request is explicit

The Python `Provider` object in `goose-sdk==0.1.0a8` exposes inference operations such as `stream()` and `complete()`, but it does not expose a public method for listing models. Therefore, this lesson creates the GDK provider to validate its declarative configuration and then queries the provider's standard OpenAI-compatible models endpoint directly.

## Step 2.1: Write the smoke test

Create `src/gdk_hello/main.py` with:

```python
import json
import sys
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import urlopen

from dotenv import load_dotenv
from goose import declarative_provider_from_json


DEFAULT_PROVIDER_CONFIG = Path("custom_aa_llama_qwen3_6-35b.json")


def main() -> None:
    load_dotenv()

    if len(sys.argv) > 2:
        raise SystemExit(
            "Usage: uv run python -m src.gdk_hello.main [provider.json]"
        )

    provider_config_path = (
        Path(sys.argv[1]) if len(sys.argv) == 2 else DEFAULT_PROVIDER_CONFIG
    )
    if not provider_config_path.exists():
        raise SystemExit(
            f"Provider configuration not found: {provider_config_path}. "
            "Run from the repository root or provide a valid JSON path."
        )

    provider_json = provider_config_path.read_text()
    provider_config = json.loads(provider_json)

    # Parse the declarative configuration with GDK. This does not make a
    # network request, but it confirms that GDK accepts the provider config.
    provider = declarative_provider_from_json(provider_json)

    models_url = f"{provider_config['base_url'].rstrip('/')}/v1/models"

    try:
        with urlopen(models_url, timeout=5) as response:
            payload = json.load(response)
    except (HTTPError, URLError) as error:
        raise SystemExit(f"Provider smoke test failed: {error}") from error

    available_models = [model["id"] for model in payload.get("data", [])]
    if not available_models:
        raise SystemExit("Provider is reachable but returned no models")

    configured_models = [model["name"] for model in provider_config["models"]]
    missing_models = sorted(set(configured_models) - set(available_models))
    if missing_models:
        raise SystemExit(
            "Provider is reachable, but configured model(s) were not found: "
            + ", ".join(missing_models)
        )

    print(f"Connected to provider: {provider.name()}")
    print("Available models:")
    for model_name in available_models:
        print(f"- {model_name}")


if __name__ == "__main__":
    main()
```

### Key ideas

- `declarative_provider_from_json(...)` verifies that GDK accepts the provider configuration.
- `load_dotenv()` makes credentials in a local `.env` available when the selected provider names an API-key environment variable.
- `GET /v1/models` is the OpenAI-compatible model discovery request used by this lesson.
- The five-second timeout makes a failed smoke test return promptly.
- Comparing configured and advertised model names catches a common configuration mismatch without making an inference request.
- No `asyncio`, `ProviderModelConfig`, `ProviderMessage`, `MessageContent`, `ProviderStream`, or `StreamChunk` code is needed yet.

## Step 2.2: Run the smoke test

From the repository root:

```bash
uv run python -m src.gdk_hello.main
```

The bundled provider JSON is the default. To use another declarative provider
configuration, pass its path as the optional positional argument:

```bash
uv run python -m src.gdk_hello.main path/to/provider.json
```

Example successful output:

```text
Connected to provider: custom_aa_llama_qwen3_6-35b
Available models:
- qwen3.6-35b-a3b
```

The exact provider name and model IDs depend on your configuration and llama.cpp server.

## Success criteria

- GDK parses the declarative provider configuration.
- The models endpoint responds successfully.
- At least one model is returned.
- Every model configured in the selected provider JSON appears in the response.

## Next

Lesson 3 makes the first inference request and introduces `ProviderModelConfig`, messages, streaming, and chunk handling.