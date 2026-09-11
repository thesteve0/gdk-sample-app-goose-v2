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


async def main():
    # Option 1: assume script is run with repo root as cwd
    # python -m src.gdk_hello.main  from project root
    load_dotenv()  # loads .env from cwd, i.e. project root
    print("Hello from gdk_hello")
    if not Path("custom_aa_llama_qwen3_6-35b.json").exists():
        raise FileNotFoundError("Run this script from the repo root with `python -m src.gdk_hello.main`")
    # Load declarative provider config for local llama.cpp
    with open("custom_aa_llama_qwen3_6-35b.json", "r") as f:
        provider_json = f.read()
    local_provider = declarative_provider_from_json(provider_json)
    default_model = ProviderModelConfig(model_name=os.getenv("MODEL_NAME"))
    messages = [
        ProviderMessage(
            role=MessageRole.USER,
            content=[MessageContent.TEXT(text="Should I build a Goose SDK application with Rust or with Python?")],
        )
    ]
    stream = await local_provider.stream(
        model=default_model,
        system="you are an expert on the goose SDK",
        messages=messages,
        tools=[],
    )
    print("Streaming response...", file=sys.stderr)
    try:
        while chunk := await stream.next_chunk():
            if isinstance(chunk, StreamChunk.TEXT_CHUNK):
                print(chunk.text, end="", flush=True)
            elif isinstance(chunk, StreamChunk.END_CHUNK) and getattr(chunk, "usage", None):
                print(f"\n\nusage: {chunk.usage}", file=sys.stderr)
            elif isinstance(chunk, StreamChunk.ERROR_CHUNK):
                print(f"\n\nerror: {chunk.error.message}", file=sys.stderr)
    except Exception as e:
        print(f"\n\nError during streaming: {e}", file=sys.stderr)
        raise
    print()



if __name__ == "__main__":
    asyncio.run(main())