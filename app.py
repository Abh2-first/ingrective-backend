from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image
import pytesseract
import io
import re

# ---------------------------------------------------------
# FASTAPI APP INITIALIZATION
# ---------------------------------------------------------
app = FastAPI(
    title="Ingrective Backend",
    description="AI-powered ingredient analyzer for food labels — Can Read and Eat 🍎",
    version="1.0.0"
)

# ---------------------------------------------------------
# CORS (allow frontend connection)
# ---------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # You can restrict this later to your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------
# SAMPLE HOMEPAGE
# ---------------------------------------------------------
@app.get("/")
def home():
    return {"message": "✅ Ingrective Backend is live and working!"}


# ---------------------------------------------------------
# HELPER FUNCTION: Extract ingredients using OCR
# ---------------------------------------------------------
def extract_ingredients_from_image(image_bytes: bytes):
    image = Image.open(io.BytesIO(image_bytes))
    text = pytesseract.image_to_string(image)
    
    # Try to locate ingredients section
    ingredients_match = re.search(r'ingredients[:\- ]?(.*)', text, re.IGNORECASE)
    if ingredients_match:
        ingredients_text = ingredients_match.group(1)
    else:
        ingredients_text = text

    # Split by commas or semicolons
    ingredients = re.split(r',|;', ingredients_text)
    ingredients = [i.strip().capitalize() for i in ingredients if len(i.strip()) > 0]
    return ingredients


# ---------------------------------------------------------
# HELPER FUNCTION: Analyze ingredients
# ---------------------------------------------------------
def analyze_ingredients(ingredients):
    harmful = ["sugar", "salt", "palm oil", "maida", "preservative", "msg", "colour", "artificial"]
    good = ["fiber", "vitamin", "protein", "calcium", "iron", "minerals"]

    analysis = {"harmful": [], "neutral": [], "good": []}

    for item in ingredients:
        i_lower = item.lower()
        if any(word in i_lower for word in harmful):
            analysis["harmful"].append(item)
        elif any(word in i_lower for word in good):
            analysis["good"].append(item)
        else:
            analysis["neutral"].append(item)

    score = max(0, 100 - len(analysis["harmful"]) * 15 + len(analysis["good"]) * 10)
    if score > 85:
        rating = "Best"
    elif score > 65:
        rating = "Better"
    else:
        rating = "Moderate"

    return {"rating": rating, "score": score, "analysis": analysis}


# ---------------------------------------------------------
# MAIN ROUTE: Analyze uploaded image
# ---------------------------------------------------------
@app.post("/analyze")
async def analyze_image(file: UploadFile = File(...)):
    try:
        image_bytes = await file.read()
        ingredients = extract_ingredients_from_image(image_bytes)
        result = analyze_ingredients(ingredients)

        return {
            "status": "success",
            "total_ingredients": len(ingredients),
            "ingredients": ingredients,
            "rating": result["rating"],
            "score": result["score"],
            "analysis": result["analysis"]
        }

    except Exception as e:
        return {"status": "error", "message": str(e)}


# ---------------------------------------------------------
# READY FOR DEPLOYMENT ✅
# ---------------------------------------------------------
# Run locally with: uvicorn app:app --reload
