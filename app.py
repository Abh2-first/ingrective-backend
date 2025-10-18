from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image
import pytesseract
import io
import difflib

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "✅ Ingrective backend is running successfully!"}


@app.post("/analyze")
async def analyze_image(file: UploadFile = File(...)):
    try:
        # Read image
        image_data = await file.read()
        image = Image.open(io.BytesIO(image_data))

        # Extract text
        extracted_text = pytesseract.image_to_string(image)
        text_lower = extracted_text.lower()

        # Ingredient lists
        harmful_ingredients = {
            "sugar": "May increase blood sugar and cause obesity risk.",
            "salt": "Too much sodium can raise blood pressure.",
            "preservative": "Can cause allergic reactions or digestion problems.",
            "artificial color": "May cause hyperactivity or allergies.",
            "artificial flavor": "Linked with migraines and chemical sensitivity.",
            "trans fat": "Increases bad cholesterol and heart risk.",
            "sodium benzoate": "May cause inflammation and oxidative stress.",
            "aspartame": "Artificial sweetener that may cause headaches.",
            "monosodium glutamate": "May cause bloating or headaches in some.",
            "high fructose corn syrup": "Can increase diabetes and fat storage risk.",
            "hydrogenated oil": "Raises cholesterol and heart disease risk."
        }

        safe_ingredients = {
            "vitamin": "Essential nutrient for body functions.",
            "fiber": "Good for digestion and gut health.",
            "protein": "Builds muscle and supports metabolism.",
            "water": "Hydrating and natural.",
            "whole grain": "Improves heart and gut health.",
            "calcium": "Strengthens bones and teeth.",
            "iron": "Supports oxygen transport in blood.",
            "magnesium": "Supports muscle and nerve functions."
        }

        # Find matches
        found_ingredients = []

        words = set(text_lower.replace(",", " ").replace(".", " ").split())

        for word in words:
            for key in harmful_ingredients:
                if difflib.get_close_matches(word, [key], cutoff=0.7):
                    found_ingredients.append({
                        "ingredient": key,
                        "status": "harmful",
                        "description": harmful_ingredients[key]
                    })
            for key in safe_ingredients:
                if difflib.get_close_matches(word, [key], cutoff=0.7):
                    found_ingredients.append({
                        "ingredient": key,
                        "status": "safe",
                        "description": safe_ingredients[key]
                    })

        if not found_ingredients:
            found_ingredients.append({
                "ingredient": "No match",
                "status": "neutral",
                "description": "No known ingredients detected. Try clearer image or text."
            })

        return {
            "text_extracted": extracted_text.strip(),
            "analysis": found_ingredients
        }

    except Exception as e:
        return {"error": str(e)}
