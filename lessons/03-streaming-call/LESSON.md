# Lesson 3: Streaming Call Deep Dive

## Goal
Build on the working streaming smoke test from Lesson 2 by understanding how each piece works under the hood. Examine `ProviderMessage` construction, chunk type checking, usage parsing, and error handling patterns in detail.

## Context
This lesson builds on Lessons 1 and 2. The same `src/gdk_hello` layout, shared venv at repo root, and `.env` / provider JSON config carry forward. Only new code is shown here; previously-created configuration files are not reproduced.

## Directory structure

```
lessons/03-streaming-call/
  LESSON.md
  src/
    gdk_hello/
      main.py          # streaming call implementation
pyproject.toml        (shared from repo root)
.env.example           (shared from repo root)
custom_aa_llama_qwen3_6-35b.json   (shared from repo root)
```

## Prerequisites
- Lessons 1–2 complete: venv with `goose-sdk`, `.env` populated, provider JSON at repo root
- llama.cpp server running and accessible

## Step 3.1: Import the right types

Open or create `src/gdk_hello/main.py` and start with these imports:

```python
import asyncio
import sys
import os
from dotenv import load_dotenv
from pathlib import Path

from goose import (
    declarative_provider_from_json,
    MessageContent,
    MessageRole,
    ProviderMessage,
    ProviderModelConfig,
    StreamChunk,
)
```

**Why these types:**
- `declarative_provider_from_json` — creates the provider from your JSON config
- `MessageContent.Text` — wraps plain-text content for a message
- `MessageRole.User` / `.Assistant` — role of the message sender
- `ProviderMessage` — carries role + content list to the provider
- `ProviderModelConfig` — model parameters (name, context limit, temperature)
- `StreamChunk.TextChunk` / `.EndChunk` / `.ErrorChunk` — response chunk variants

## Step 3.2: Build a ProviderMessage list

Each conversation turn is a list of `ProviderMessage`. For the first message from the user:

```python
messages = [
    ProviderMessage(
        role=MessageRole.USER,
        content=[MessageContent.Text(text="Should I build a Goose SDK application with Rust or with Python?")],
    )
]
```

**Key details:**
- `role` is an enum: `MessageRole.User`, `MessageRole.Assistant`, or `MessageRole.Tool`
- `content` is a **list** of `MessageContent` variants (supports text + images in one message)
- Use `MessageContent.Text(text=...)` for plain text — not `.TEXT()`. The Python bindings expose the Rust enum variant name (`Text`) directly as an attribute

Reference: [bindings.rs MessageContent](https://github.com/aaif-goose/goose/blob/main/crates/goose-sdk/src/bindings.rs) (enum `MessageContent` with variant `Text { text: String }`)

## Step 3.3: Create the provider and model config

Load your declarative config and build a `ProviderModelConfig`:

```python
provider = declarative_provider_from_json(Path("custom_aa_llama_qwen3_6-35b.json").read_text())
model = ProviderModelConfig(model_name=os.getenv("MODEL_NAME"))
```

**Note:** `OPENAI_BASE_URL` and auth come from the JSON config file. The `ProviderModelConfig` is for model parameters only (name, context limit, temperature, max tokens).

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
    if isinstance(chunk, StreamChunk.TextChunk):
        print(chunk.text, end="", flush=True)
    elif isinstance(chunk, StreamChunk.EndChunk) and chunk.usage:
        print(f"\n\nusage: {chunk.usage}", file=sys.stderr)
    elif isinstance(chunk, StreamChunk.ErrorChunk):
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
| `StreamChunk.TextChunk` | `.text: str` — a fragment of the model's reply | Each turn during generation |
| `StreamChunk.EndChunk` | `.usage: Optional[Usage]` — token counts, model name | Once at stream end |
| `StreamChunk.ErrorChunk` | `.error.message: str` — error description | If a provider error occurs |

Other chunk variants exist (`ThinkingChunk`, `RedactedThinkingChunk`, `ToolChunk`) but are not needed for this basic smoke test. Reference: [bindings.rs StreamChunk](https://github.com/aaif-goose/goose/blob/main/crates/goose-sdk/src/bindings.rs) (enum `StreamChunk`)

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
import sys
import os
from dotenv import load_dotenv
from pathlib import Path

from goose import (
    declarative_provider_from_json,
    MessageContent,
    MessageRole,
    ProviderMessage,
    ProviderModelConfig,
    StreamChunk,
)


async def main() -> None:
    load_dotenv()
    if not Path("custom_aa_llama_qwen3_6-35b.json").exists():
        raise FileNotFoundError(
            "Run this script from the repo root with "
            "`python -m src.gdk_hello.main`"
        )

    # Load provider and model config
    provider = declarative_provider_from_json(
        Path("custom_aa_llama_qwen3_6-35b.json").read_text()
    )
    model = ProviderModelConfig(model_name=os.getenv("MODEL_NAME"))

    # Build the user message
    messages = [
        ProviderMessage(
            role=MessageRole.USER,
            content=[
                MessageContent.Text(
                    text="Should I build a Goose SDK application with Rust or with Python?"
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

    try:
        while chunk := await stream.next_chunk():
            if isinstance(chunk, StreamChunk.TextChunk):
                print(chunk.text, end="", flush=True)
            elif isinstance(chunk, StreamChunk.EndChunk) and chunk.usage:
                print(f"\n\nusage: {chunk.usage}", file=sys.stderr)
            elif isinstance(chunk, StreamChunk.ErrorChunk):
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

## Step 3.6: Run the script

From repo root:

```bash
cd /var/home/stpousty/git/gdk-sample-app-goose-build-v2
uv run python -m src.gdk_hello.main
```

**Expected output:**
- stderr (in `[2m` brackets): `Streaming response...`
- stdout: The model's streaming reply as plain text
- stderr (at end): `usage:` line with token counts

If the server is down or the model name doesn't match, you'll see an `ErrorChunk` instead of text.

## Best practices

- Always wrap stream logic in a try/except — network errors are common during development
- Print non-text output (usage, errors) to stderr so stdout stays clean for captured text
- Use `flush=True` with streaming text to avoid buffering delays
- Keep `system`, `messages`, and `tools` as separate arguments — don't concatenate them
- The `tools=[]` argument is required; an empty list is correct when no tools are defined (Lesson 5 covers tool definitions)

## Reference

- SDK source: https://github.com/aaif-goose/goose/blob/main/crates/goose-sdk/src/bindings.rs
- Python example (canonical): https://github.com/aaif-goose/goose/blob/main/crates/goose-sdk/examples/uniffi/provider.py
- `StreamChunk` enum definition: [bindings.rs lines 554–580](https://github.com/aaif-goose/goose/blob/main/crates/goose-sdk/src/bindings.rs)
- `MessageContent` enum definition: [bindings.rs lines 198–237](https://github.com/aaif-goose/goose/blob/main/crates/goose-sdk/src/bindings.rs)

## Next steps
Once you understand the streaming fundamentals:
- Lesson 4: System prompt and message roles — add multi-turn conversation with assistant responses
- Lesson 5: Add first `ProviderTool` definition — enable the model to call custom functions
- Lesson 6: Tool execution loop — parse tool requests from chunks, execute tools, send results back

## Questions to ask before proceeding
- Does your llama.cpp server return text chunks correctly?
- Can you see usage stats in the `EndChunk` output?
- Do you want multi-turn conversation (Lesson 4) or tool support (Lesson 5) next?
