import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()  # loads GOOGLE_API_KEY from your .env
api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    raise RuntimeError("GOOGLE_API_KEY is missing in environment variables/.env file")

genai.configure(api_key=api_key)

print("Available Gemini models:")
for model in genai.list_models():
    print("-", model.name)