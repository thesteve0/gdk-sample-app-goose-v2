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

    # The provider JSON configures the endpoint and lists its available models,
    # while ProviderModelConfig selects a model for this request. The SDK needs
    # both because it does not implicitly select the first model in the list.
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
