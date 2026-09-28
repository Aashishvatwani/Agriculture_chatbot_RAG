import os
import requests
from dotenv import load_dotenv

load_dotenv()  # loads OPENROUTER_API_KEY from your .env

api_key = os.getenv("OPENROUTER_API_KEY")

if not api_key:
    raise RuntimeError("OPENROUTER_API_KEY is missing in environment variables/.env file")

print("Testing OpenRouter API connection...")
print(f"Using API key ending in ...{api_key[-4:]}")

# Make a simple test request
response = requests.post(
    "https://openrouter.ai/api/v1/chat/completions",
    headers={
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost:8000",
        "X-Title": "AgriSearch Bot Test",
    },
    json={
        "model": os.getenv("OPENROUTER_MODEL", "qwen/qwen3.8-27b:free"),
        "messages": [
            {"role": "user", "content": "Say hello in one sentence."}
        ],
        "max_tokens": 50,
    },
    timeout=30,
)

if response.status_code == 200:
    data = response.json()
    reply = data["choices"][0]["message"]["content"]
    model_used = data.get("model", "unknown")
    print(f"\n[OK] OpenRouter API working!")
    print(f"   Model: {model_used}")
    print(f"   Reply: {reply}")
else:
    print(f"\n[ERROR] OpenRouter API error: {response.status_code}")
    print(f"   Response: {response.text}")