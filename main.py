import os
import json
import io
from PIL import Image
import google.generativeai as genai
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from pydantic import BaseModel
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI(title="NOVA / MJ AI Assistant API - All Features")

# Gemini API Setup
GEMINI_API_KEY = os.getenv("AIzaSyCgO0B18KvsqKE4Qz3IBr8oGBXPifSk-6M")
genai.configure(api_key=GEMINI_API_KEY)

# Using Gemini 1.5 Flash as it supports both Text and Vision efficiently
model = genai.GenerativeModel('gemini-1.5-flash')

class TextCommand(BaseModel):
    command: str

@app.get("/")
def home():
    return {"status": "AI Master Server is Running Successfully! 🚀", "version": "5.0"}

# ==========================================
# ROUTE 1: Text & Voice Commands (System, Spotify, Files)
# ==========================================
@app.post("/api/command")
async def process_text_command(req: TextCommand):
    system_prompt = f"""
    You are the core intelligence of an advanced Android Assistant.
    The user command is: "{req.command}"
    
    You must output ONLY a valid JSON object. No markdown, no explanations.
    Analyze the command and return the appropriate action structure:

    1. System App/Settings Open:
       {{"action": "open_system_app", "app_name": "whatsapp/settings/camera/youtube"}}
    2. Spotify Control:
       {{"action": "play_spotify", "song": "song_name", "artist": "artist_name"}}
    3. File Management (Create/Copy/Move):
       {{"action": "file_manager", "operation": "create", "path": "/storage/emulated/0/Download", "filename": "name.txt"}}
    4. System Analysis/Device Info:
       {{"action": "system_analysis", "task": "check_battery_or_storage"}}
    5. General Chat/Answers:
       {{"action": "speak", "text": "Your conversational answer here in Hindi/English"}}
    """

    try:
        response = model.generate_content(system_prompt)
        raw_text = response.text.strip().removeprefix('```json').removesuffix('```').strip()
        return {"status": "success", "data": json.loads(raw_text)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==========================================
# ROUTE 2: Vision & Screen Processing (Screen, Image, Camera Analysis)
# ==========================================
@app.post("/api/vision")
async def process_vision_command(
    feature_type: str = Form(...), # 'screen_reading', 'screen_analysis', 'camera_analysis', 'image_analysis'
    user_prompt: str = Form(default="Analyze this image and tell me what you see."),
    image: UploadFile = File(...)
):
    try:
        # Image ko read karke PIL format me convert karna
        image_data = await image.read()
        pil_image = Image.open(io.BytesIO(image_data))

        # Alag-alag features ke liye prompts
        if feature_type == "screen_reading":
            prompt = "Extract all readable text and UI elements from this screenshot. Return output as a JSON with key 'extracted_text'."
        elif feature_type == "screen_analysis":
            prompt = "Analyze this Android screen. What app is open? What is the user doing? Return JSON with keys 'current_app' and 'activity_description'."
        elif feature_type == "camera_analysis":
            prompt = f"This is a live camera feed. {user_prompt}. Return JSON with key 'surroundings_analysis'."
        else:
            prompt = f"Analyze this image. {user_prompt}. Return JSON with key 'image_details'."

        prompt += "\nOutput ONLY valid JSON."

        # Vision model ko image aur prompt bhejna
        response = model.generate_content([prompt, pil_image])
        raw_text = response.text.strip().removeprefix('```json').removesuffix('```').strip()

        return {"status": "success", "feature": feature_type, "data": json.loads(raw_text)}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
