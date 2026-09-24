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