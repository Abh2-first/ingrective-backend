from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image
import pytesseract
import io
import difflib

app = FastAPI()

# Allow requests from your frontend (Vercel)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # You can later replace "*" with your Vercel URL for security
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Basic ingredient lists
healthy_ingredients = ["oats", "almond", "brown rice", "flaxseed", "olive oil", "green tea"]
unhealthy_ingredients = ["sugar", "corn syrup", "palm oil", "sodium", "preservative", "maida", "trans fat"]

@app.get("/")
def home():
    return {"message": "Ingrective backend is working!"}

@app.post("/analyze")
async def analyze_image(file: UploadFile = File(...)):
    # Read uploaded image
    contents = await file.read()
    image = Image.open(io.BytesIO(contents))

    # OCR: extract text from image
    extracted_text = pytesseract.image_to_string(image).lower()

    # Analyze ingredients
    result = []
    for word in extracted_text.split():
        close_healthy = difflib.get_close_matches(word, healthy_ingredients, n=1, cutoff=0.8)
        close_unhealthy = difflib.get_close_matches(word, unhealthy_ingredients, n=1, cutoff=0.8)
        if close_healthy:
            result.append({"ingredient": word, "type": "Healthy ✅"})
        elif close_unhealthy:
            result.append({"ingredient": word, "type": "Unhealthy ❌"})

    return {
        "status": "success",
        "extracted_text": extracted_text,
        "analysis": result
    }
