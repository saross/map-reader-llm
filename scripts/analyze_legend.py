import google.generativeai as genai
from PIL import Image
from pathlib import Path
import sys

# Adjust python path
sys.path.append(str(Path(__file__).parent.parent))
from config import GOOGLE_API_KEY, MODEL_NAME

def describe_legend():
    if not GOOGLE_API_KEY:
        print("Error: GOOGLE_API_KEY not found.")
        return

    genai.configure(api_key=GOOGLE_API_KEY)
    
    # Use the same model we are testing
    model = genai.GenerativeModel("gemini-3-pro-preview")
    
    legend_path = Path(__file__).parent.parent / "inputs" / "legend.tif"
    if not legend_path.exists():
        print("Legend file not found.")
        return

    # Convert to PNG for API
    img_pil = Image.open(legend_path)
    if img_pil.mode == 'CMYK':
        img_pil = img_pil.convert('RGB')
    
    temp_png = Path("temp_legend.png")
    img_pil.save(temp_png, format="PNG")
    img = Image.open(temp_png)
    
    prompt = """
    Analyze this map legend. Provide concise visual descriptions for the following 4 symbols:
    1. "Burial mound" (Tumulus)
    2. "Settlement mound" (might be listed as 'Ancient settlement' or similar)
    3. "Triangulation point on a settlement mound"
    4. "Bench mark on a burial mound"
    
    For each, describe the shape, color (if distinguishable, otherwise assume standard brown/black for topography), and key distinguishing features (e.g., "star shape", "triangle with dot", "rays").
    """
    
    print("Asking Gemini to describe the legend symbols...")
    try:
        response = model.generate_content([prompt, img])
        print(response.text)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    describe_legend()
