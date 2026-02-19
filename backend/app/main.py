from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os

# --- CHANGED THIS IMPORT ---
from app.services.message_engine import generate_note
from app.services.scribe import overlay_message

app = FastAPI()

# --- CORS ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- MOUNT FOLDERS ---
app.mount("/assets", StaticFiles(directory="assets"), name="assets")
app.mount("/generated", StaticFiles(directory="static/generated"), name="generated")

# --- DATA MODELS ---
class BouquetRequest(BaseModel):
    flower_id: str

class MessageRequest(BaseModel):
    recipient: str
    flower_id: str

class SignRequest(BaseModel):
    image_url: str
    message_text: str

# --- ROUTES ---

@app.post("/api/generate-bouquet")
async def get_bouquet(request: BouquetRequest):
    flower_id = request.flower_id.lower()
    
    # Check if we have the image
    image_path = f"assets/bouquets/{flower_id}.png"
    if not os.path.exists(image_path):
        print(f"Warning: {image_path} not found.")
        # Fallback for testing if you haven't downloaded images yet
        # raise HTTPException(status_code=404, detail="Bouquet not found")
    
    return {
        "image_url": f"/assets/bouquets/{flower_id}.png",
        "status": "success"
    }

@app.post("/api/generate-message")
async def api_gen_message(request: MessageRequest):
    # Uses the new OpenAI engine
    note = generate_note(request.recipient, request.flower_id)
    return {"message": note}

@app.post("/api/add-note")
async def api_add_note(request: SignRequest):
    final_url = overlay_message(request.image_url, request.message_text)
    if not final_url:
        raise HTTPException(status_code=500, detail="Failed to sign card")
    return {"final_image_url": final_url}