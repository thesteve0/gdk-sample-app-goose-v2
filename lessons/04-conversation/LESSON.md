# Lesson 4: System Instructions and Conversation History

## Goal

Extend the one-message streaming request from Lesson 3 into a two-turn conversation. Keep system instructions separate from conversation messages, capture the first streamed assistant reply, and send the complete history with a follow-up user message.

## Concepts introduced

- The different jobs of the `system` argument and `ProviderMessage` roles.
- `MessageRole.USER` and `MessageRole.ASSISTANT` in conversation history.
- Capturing streamed text while still printing it as it arrives.
- Re-sending prior turns because each provider call receives an explicit message list.

## Context

This lesson builds directly on Lesson 3. Provider loading, first-model selection, and chunk handling stay the same so the focus remains on conversation structure.

The complete reference solution is in:

```text
lessons/04-conversation/
  LESSON.md
  src/
    gdk_hello/
      __init__.py
      main.py
```

The shared `pyproject.toml`, lockfile, `.env`, and provider JSON remain at the repository root.

## Prerequisites

- Lessons 1–3 complete.
- `goose-sdk==0.1.0a9` installed through `uv sync`.
- A compatible streaming provider running and accessible.
- The selected provider JSON declares at least one model.

## Step 4.1: Name the system instruction

In Lesson 3, `provider.stream(...)` already received a short `system` string. Give that instruction a name and make its purpose visible:

```python
SYSTEM_INSTRUCTION = (
    "You are a concise programming instructor. "
    "Answer in no more than three sentences."
)
```

The system instruction sets behavior for the request. It is not a user or assistant turn, so do not add it to the `messages` list.

Pass it separately on every call:

```python
stream = await provider.stream(
    model=model,
    system=SYSTEM_INSTRUCTION,
    messages=messages,
    tools=[],
)
```

This application makes two provider calls. Reusing the same value keeps the instruction active for both calls.

## Step 4.2: Return the streamed assistant text

Lesson 3 prints text chunks and then discards them. A conversation needs the assistant's first reply in its history, so collect each fragment while continuing to display it:

```python
text_parts: list[str] = []

while chunk := await stream.next_chunk():
    if isinstance(chunk, StreamChunk.TEXT_CHUNK):
        text_parts.append(chunk.text)
        print(chunk.text, end="", flush=True)
```

After the stream reaches its end chunk, join the fragments:

```python
return "".join(text_parts)
```

Extract that logic into an async helper:

```python
async def stream_response(provider, model, messages: list[ProviderMessage]) -> str:
    ...
```

The helper should preserve Lesson 3's structural checks: at least one text chunk must arrive, and normal completion must include an end chunk.

## Step 4.3: Start with one user message

The first request still begins with a user turn:

```python
messages = [
    ProviderMessage(
        role=MessageRole.USER,
        content=[
            MessageContent.TEXT(
                text="Should I build a Goose SDK application with Rust or Python?"
            )
        ],
    )
]
```

Call the helper and keep the returned text:

```python
first_response = await stream_response(provider, model, messages)
```

## Step 4.4: Add the assistant reply and follow-up

Append the generated response as an assistant message, followed by the next user message:

```python
messages.extend(
    [
        ProviderMessage(
            role=MessageRole.ASSISTANT,
            content=[MessageContent.TEXT(text=first_response)],
        ),
        ProviderMessage(
            role=MessageRole.USER,
            content=[
                MessageContent.TEXT(
                    text="Summarize your recommendation in five words or fewer."
                )
            ],
        ),
    ]
)
```

The list is now ordered as:

1. User asks the original question.
2. Assistant gives the streamed answer.
3. User asks a context-dependent follow-up.

Send that entire list in the second call:

```python
await stream_response(provider, model, messages)
```

The application—not the provider object—builds the history supplied to each request. Omitting the assistant turn would remove the answer that “your recommendation” refers to.

`MessageRole.TOOL` exists, but it belongs to the tool-result round trip introduced in a later lesson.

## Step 4.5: Run the conversation

From the repository root, update the active exercise as directed by the instructor and run:

```bash
uv run python -m src.gdk_hello.main
```

To use another declarative provider configuration:

```bash
uv run python -m src.gdk_hello.main path/to/provider.json
```

## Expected structural behavior

- The first assistant response streams to stdout and is captured in memory.
- Usage is printed to stderr when the provider supplies it.
- The captured text is added as a `MessageRole.ASSISTANT` message.
- The second request receives all three messages in order.
- A second assistant response streams to stdout.
- Both requests use the same system instruction.

Generated wording is nondeterministic. The second answer should respond to the follow-up in the context of the first exchange, but it may not obey the requested word count exactly.

## Success criteria

- Both provider calls return at least one text chunk and reach an end chunk.
- The first assistant response is reconstructed from streamed fragments.
- Conversation history contains user, assistant, and follow-up user turns in that order.
- The system instruction remains separate from `messages` and is supplied to both calls.
- No exact generated wording is required.

## Check your understanding

- Why must the first assistant response be added to the second request's message list?
- Why is the system instruction passed separately instead of using another message role?
- Why collect chunks in a list and join them only after streaming ends?
- Which parts of the second call are new, and which parts are unchanged from Lesson 3?

## Next

Lesson 5 adds explicit model selection. Instead of always choosing the first model declared by the provider JSON, the application will accept a model name and validate it against the configured models.

## References

- [Goose SDK Python provider example](https://github.com/aaif-goose/goose/blob/13f4d26e1e70/crates/goose-sdk/examples/uniffi/provider.py)
- [Goose SDK provider bindings](https://github.com/aaif-goose/goose/blob/13f4d26e1e70/crates/goose-sdk/src/bindings.rs)
