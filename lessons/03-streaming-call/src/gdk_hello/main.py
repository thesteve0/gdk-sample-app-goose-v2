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
