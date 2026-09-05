import os
from dotenv import load_dotenv
from goose import openai_provider
from goose import ProviderModelConfig

def main():
    load_dotenv()
    print("Hello from gdk_hello")
    provider_config = ProviderModelConfig(model_name=os.getenv("MODEL_NAME"), api_key=os.getenv("OPENAI_API_KEY"), base_url=(os.getenv("OPENAI_BASE_URL")))

if __name__ == "__main__":
    main()