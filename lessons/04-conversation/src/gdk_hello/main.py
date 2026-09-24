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
SYSTEM_INSTRUCTION = (
    "You are a concise programming instructor. "
    "Answer in no more than three sentences."
)


async def stream_response(provider, model, messages: list[ProviderMessage]) -> str:
    stream = await provider.stream(
        model=model,
        system=SYSTEM_INSTRUCTION,
        messages=messages,
        tools=[],
    )

    text_parts: list[str] = []
    saw_end = False
    while chunk := await stream.next_chunk():
        if isinstance(chunk, StreamChunk.TEXT_CHUNK):
            text_parts.append(chunk.text)
            print(chunk.text, end="", flush=True)
        elif isinstance(chunk, StreamChunk.END_CHUNK):
            saw_end = True
            if chunk.usage:
                print(f"\nusage: {chunk.usage}", file=sys.stderr)
        elif isinstance(chunk, StreamChunk.ERROR_CHUNK):
            raise RuntimeError(chunk.error.message)

    if not text_parts:
        raise RuntimeError("The stream completed without returning text")
    if not saw_end:
        raise RuntimeError("The stream ended without an end chunk")

    print()
    return "".join(text_parts)


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
    provider = declarative_provider_from_json(provider_json)
    model = ProviderModelConfig(
        model_name=provider_config["models"][0]["name"]
    )

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

    print("Assistant (turn 1):")
    first_response = await stream_response(provider, model, messages)

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

    print("\nAssistant (turn 2):")
    await stream_response(provider, model, messages)


if __name__ == "__main__":
    asyncio.run(main())
