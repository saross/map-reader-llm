
import google.generativeai as genai
import sys
import os

# Add parent directory to path to find config
sys.path.append(os.getcwd())
from config import GOOGLE_API_KEY

if not GOOGLE_API_KEY:
    print("Error: GOOGLE_API_KEY not found.")
    sys.exit(1)

genai.configure(api_key=GOOGLE_API_KEY)

print("Available Models:")
try:
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(f"- {m.name}")
except Exception as e:
    print(f"Error listing models: {e}")
