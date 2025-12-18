import google.generativeai as genai
import sys
from pathlib import Path

# Add parent directory to path to import config
sys.path.append(str(Path(__file__).parent.parent.parent))
from config import GOOGLE_API_KEY

if not GOOGLE_API_KEY:
    print("Error: GOOGLE_API_KEY missing")
    sys.exit(1)

genai.configure(api_key=GOOGLE_API_KEY)

print("Listing available models...")
try:
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(f"- {m.name}")
except Exception as e:
    print(f"Error listing models: {e}")
