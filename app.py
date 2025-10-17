from fastapi import FastAPI, UploadFile, File

app = FastAPI()

@app.get("/")
def home():
    return {"message": "✅ Ingrective Backend is live and working!"}

from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
from PIL import Image
import requests, io, re

app = FastAPI()

HF_API_URL = "https://api-inference.huggingface.co/models/microsoft/trocr-base-printed"
HF_TOKEN = "hf_your_token_here"   # add your token in Render environment

harmful = ["sugar","palm oil","msg","aspartame"]
healthy = ["oats","almonds","honey","olive oil"]
neutral = ["salt","water","wheat","rice"]

def hf_ocr(img_bytes):
    r = requests.post(
        HF_API_URL,
        headers={"Authorization": f"Bearer {HF_TOKEN}"},
        data=img_bytes,
    )
    j = r.json()
    return j[0]["generated_text"] if isinstance(j, list) else ""

@app.post("/analyze")
async def analyze(file: UploadFile = File(...)):
    img_bytes = await file.read()
    text = hf_ocr(img_bytes)
    match = re.search(r"ingredients[:\-]?(.*)", text, re.IGNORECASE)
    part = match.group(1) if match else text
    items = [i.strip().lower() for i in re.split(r",|;", part) if i.strip()]
    analyzed, score = [], 0
    for it in items:
        if any(x in it for x in harmful):
            analyzed.append({"name": it,"category":"red"}); score -= 2
        elif any(x in it for x in healthy):
            analyzed.append({"name": it,"category":"green"}); score += 2
        else:
            analyzed.append({"name": it,"category":"neutral"})
    final = max(0,min(100,50+score*3))
    return JSONResponse({"ingredients": analyzed, "overall_score": final})
