# Lesson 3: First Streaming Call

## Goal
Build on Lesson 2's provider connectivity check by making the first inference request. Introduce the minimum message construction, model selection, and stream handling needed to receive a response; later lessons deepen message roles and multi-turn conversations.

## Context
This lesson builds on Lessons 1 and 2. The same `src/gdk_hello` layout, shared environment at the repository root, and provider JSON carry forward. Only new code is shown here; previously-created configuration files are not reproduced.

## Directory structure

```
lessons/03-streaming-call/
  LESSON.md
  src/
    gdk_hello/
      main.py          # streaming call implementation
pyproject.toml        (shared from repo root)
custom_aa_llama_qwen3_6-35b.json   (shared from repo root)
```

## Prerequisites
- Lessons 1–2 complete: environment with `goose-sdk` and provider JSON at the repository root
- A compatible provider running and accessible

## Step 3.1: Import the right types

Open or create `src/gdk_hello/main.py` and start with these imports:

```python
import asyncio
import json
import sys
from pathlib import Path

from dotenv import load_dotenv
from goose import (
    declarative_provider_from_json,
    MessageContent,
    MessageRole,
    ProviderMessage,
    ProviderModelConfig,
    StreamChunk,
)


DEFAULT_PROVIDER_CONFIG = Path("custom_aa_llama_qwen3_6-35b.json")
```

**Why these types:**
- `declarative_provider_from_json` — creates the provider from your JSON config
- `MessageContent.TEXT` — wraps plain-text content for a message
- `MessageRole.USER` — marks this first message as user input
- `ProviderMessage` — carries a role and content list to the provider
- `ProviderModelConfig` — selects the model and can carry request-specific model settings
- `StreamChunk.TEXT_CHUNK` / `.END_CHUNK` / `.ERROR_CHUNK` — response chunk variants

## Step 3.2: Build a ProviderMessage list

Each conversation turn is a list of `ProviderMessage`. For the first message from the user:

```python
messages = [
    ProviderMessage(
        role=MessageRole.USER,
        content=[
            MessageContent.TEXT(
                text=(
                    "Should I build a Goose SDK application with Rust or with Python? "
                    "Answer in no more than three sentences."
                )
            )
        ],
    )
]
```

**Key details:**
- This first request uses `MessageRole.USER`; Lesson 4 introduces assistant messages and conversation history.
- `content` is a **list** of `MessageContent` variants, so one message can carry more than one content block.
- Use `MessageContent.TEXT(text=...)` for plain text in `goose-sdk==0.1.0a9`.

Reference: [the `goose-sdk==0.1.0a9` bindings](https://github.com/aaif-goose/goose/blob/13f4d26e1e70/crates/goose-sdk/src/bindings.rs) define `MessageContent` with a Rust `Text { text: String }` variant; the published Python wheel exposes that variant as `MessageContent.TEXT`.

## Step 3.3: Create the provider and model config

Load your declarative config and build a `ProviderModelConfig`:

```python
provider_json = DEFAULT_PROVIDER_CONFIG.read_text()
provider_config = json.loads(provider_json)
provider = declarative_provider_from_json(provider_json)
model = ProviderModelConfig(model_name=provider_config["models"][0]["name"])
```

**Note:** The provider endpoint, authentication behavior, and available model definitions come from the JSON config file. `ProviderModelConfig` selects one of those models for this request. This lesson deliberately uses the first configured model; a later lesson adds explicit model selection.

## Step 3.4: Call stream() and iterate chunks

The provider's `stream()` method returns a `ProviderStream`. It's async — use `await`:

```python
stream = await provider.stream(
    model=model,
    system="you are an expert on the goose SDK",
    messages=messages,
    tools=[],
)
print("Streaming response...", file=sys.stderr)
```

Iterate over chunks. The stream returns one chunk at a time until it's exhausted:

```python
while chunk := await stream.next_chunk():
    if isinstance(chunk, StreamChunk.TEXT_CHUNK):
        print(chunk.text, end="", flush=True)
    elif isinstance(chunk, StreamChunk.END_CHUNK) and chunk.usage:
        print(f"\n\nusage: {chunk.usage}", file=sys.stderr)
    elif isinstance(chunk, StreamChunk.ERROR_CHUNK):
        print(f"\n\nerror: {chunk.error.message}", file=sys.stderr)
```

**How the stream works:**
1. `stream.next_chunk()` is an **async** call — always `await` it
2. Each chunk is one of several variants (checked with `isinstance`)
3. Text flows through `TextChunk` — append or print directly
4. When finished, an `EndChunk` arrives (optionally carrying `Usage`)
5. If the server returns an error mid-stream, an `ErrorChunk` appears

### Chunk types

| Variant | What it carries | When it arrives |
|---|---|---|
| `StreamChunk.TEXT_CHUNK` | `.text: str` — a fragment of the model's reply | During generation |
| `StreamChunk.END_CHUNK` | `.usage: Optional[Usage]` — token counts, model name | Once at stream end |
| `StreamChunk.ERROR_CHUNK` | `.error.message: str` — error description | If a provider error occurs |

Other chunk variants exist for thinking and tool calls, but are not needed for this first streaming request. See the [`goose-sdk==0.1.0a9` `StreamChunk` definition](https://github.com/aaif-goose/goose/blob/13f4d26e1e70/crates/goose-sdk/src/bindings.rs#L553-L575).

### Usage object fields

When present on `EndChunk.usage`:
- `input_tokens` — tokens consumed by your input
- `output_tokens` — tokens generated
- `total_tokens` — sum of above
- `model` — model name used
- `provider_metadata_json` — raw provider-specific data as JSON

## Step 3.5: Full implementation

Put it all together in an async `main()`:

```python
import asyncio
import json
import sys
from pathlib import Path

from dotenv import load_dotenv
from goose import (
    declarative_provider_from_json,
    MessageContent,
    MessageRole,
    ProviderMessage,
    ProviderModelConfig,
    StreamChunk,
)


DEFAULT_PROVIDER_CONFIG = Path("custom_aa_llama_qwen3_6-35b.json")


async def main() -> None:
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

    # Load the provider and select the first model declared by its config.
    provider = declarative_provider_from_json(provider_json)
    model = ProviderModelConfig(
        model_name=provider_config["models"][0]["name"]
    )

    # Build the user message
    messages = [
        ProviderMessage(
            role=MessageRole.USER,
            content=[
                MessageContent.TEXT(
                    text=(
                        "Should I build a Goose SDK application with Rust or with Python? "
                        "Answer in no more than three sentences."
                    )
                )
            ],
        )
    ]

    # Stream the response
    stream = await provider.stream(
        model=model,
        system="you are an expert on the goose SDK",
        messages=messages,
        tools=[],
    )
    print("Streaming response...", file=sys.stderr)

    saw_text = False
    saw_end = False
    try:
        while chunk := await stream.next_chunk():
            if isinstance(chunk, StreamChunk.TEXT_CHUNK):
                saw_text = True
                print(chunk.text, end="", flush=True)
            elif isinstance(chunk, StreamChunk.END_CHUNK):
                saw_end = True
                if chunk.usage:
                    print(f"\n\nusage: {chunk.usage}", file=sys.stderr)
            elif isinstance(chunk, StreamChunk.ERROR_CHUNK):
                raise RuntimeError(chunk.error.message)
    except Exception as e:
        print(f"\n\nError during streaming: {e}", file=sys.stderr)
        raise

    if not saw_text:
        raise RuntimeError("The stream completed without returning text")
    if not saw_end:
        raise RuntimeError("The stream ended without an end chunk")
    print()


if __name__ == "__main__":
    asyncio.run(main())
```

## Step 3.6: Run the script

From the repository root:

```bash
uv run python -m src.gdk_hello.main
```

To override the bundled provider configuration:

```bash
uv run python -m src.gdk_hello.main path/to/provider.json
```

**Expected output:**
- stderr (in `[2m` brackets): `Streaming response...`
- stdout: The model's streaming reply as plain text
- stderr (at end): `usage:` line with token counts

If the provider reports an error after streaming starts, it may arrive as an `ErrorChunk`. Connection and setup failures can also be raised directly by `provider.stream(...)` or `stream.next_chunk()`.

## Success criteria

- GDK loads the selected provider JSON.
- The request uses the first model declared by that configuration.
- At least one text chunk is printed to stdout.
- The stream reaches normal completion; usage is printed when the provider supplies it.
- No specific generated wording is required.

## Best practices

- Keep stream errors visible; this lesson logs an error before re-raising it rather than treating a partial response as success.
- Print non-text output (usage, errors) to stderr so stdout stays clean for captured text.
- Use `flush=True` with streaming text to avoid buffering delays
- Keep `system`, `messages`, and `tools` as separate arguments — don't concatenate them
- The `tools=[]` argument is required; an empty list is correct when no tools are defined (Lesson 6 covers tool definitions).

## Reference

- [`goose-sdk==0.1.0a9` provider bindings](https://github.com/aaif-goose/goose/blob/13f4d26e1e70/crates/goose-sdk/src/bindings.rs)
- [`goose-sdk==0.1.0a9` Python provider example](https://github.com/aaif-goose/goose/blob/13f4d26e1e70/crates/goose-sdk/examples/uniffi/provider.py)

## Next steps

Lesson 4 separates system instructions from conversation messages, captures the first assistant response, and sends a follow-up request with the complete two-turn history. Explicit `--model` selection follows in Lesson 5; tools begin in Lesson 6.

## Check your understanding

- Does your provider return text chunks correctly?
- Can you identify whether it supplies usage data in the `EndChunk`?
- Why does this lesson select the first configured model instead of reading a model name from `.env`?