import os
import json
from pathlib import Path
from google.genai import Client

def load_api_key():
    key = os.environ.get("GOOGLE_API_KEY")
    if key:
        return key
    config_path = Path.home() / ".config" / "opencode" / "opencode.json"
    if config_path.exists():
        with open(config_path) as f:
            config = json.load(f)
        return config["provider"]["google"]["options"]["apiKey"]
    raise RuntimeError("GOOGLE_API_KEY not found")

def test_model(client, model_name, prompt):
    print(f"Testing {model_name}...")
    try:
        response = client.models.generate_content(
            model=model_name,
            contents=prompt,
        )
        print(f"SUCCESS! Response: {response.text[:100]}...")
        return True
    except Exception as e:
        print(f"FAILED! Error: {e}")
        return False

def main():
    try:
        api_key = load_api_key()
        client = Client(api_key=api_key)
        
        print("--- Basic Connectivity Test ---")
        test_model(client, "gemini-2.5-flash", "Say 'Hello, world!'")
        test_model(client, "gemini-2.5-pro", "Say 'Hello, world!'")
        
        print("\n--- Translation Test (Small) ---")
        dutch_text = "In den beginne schiep God den hemel en de aarde."
        prompt = f"Translate this to English: {dutch_text}"
        test_model(client, "gemini-2.5-flash", prompt)
        
    except Exception as e:
        print(f"Setup failed: {e}")

if __name__ == "__main__":
    main()
