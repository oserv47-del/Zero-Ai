import os
import json
import google.generativeai as genai
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv

# Load environment variables (Local testing ke liye)
load_dotenv()

app = FastAPI(title="AI Personal Assistant API")

# Setup Gemini API (Free Tier)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    print("Warning: GEMINI_API_KEY is not set!")

genai.configure(api_key=GEMINI_API_KEY)

# Hum gemini-1.5-flash use karenge kyunki ye fast aur free tier me available hai
model = genai.GenerativeModel('gemini-1.5-flash')

# Request Body Structure
class UserCommand(BaseModel):
    command: str

@app.get("/")
def home():
    return {"status": "AI API is Live!", "version": "1.0"}

@app.post("/api/process")
async def process_user_command(req: UserCommand):
    # AI ko sikhane ke liye System Prompt (Taaki wo sirf JSON de)
    system_prompt = f"""
    You are the brain of an Android personal assistant. 
    The user said this command in Hindi/English: "{req.command}"
    
    Understand the command and return ONLY a valid JSON object. Do not add markdown like ```json.
    
    Rules for JSON output:
    1. If user wants to create a file: 
       {{"action": "create_file", "folder_path": "path_mentioned_or_default", "file_name": "name.txt"}}
    2. If user wants to copy a folder:
       {{"action": "copy_folder", "source_path": "source", "destination_path": "destination"}}
    3. If user wants to play a song:
       {{"action": "play_music", "song_name": "name"}}
    4. If it is a normal question or conversation:
       {{"action": "speak", "text": "Your answer in Hindi/Hinglish"}}
    """

    try:
        # AI se response lena
        response = model.generate_content(system_prompt)
        
        # AI kabhi-kabhi ```json tag laga deta hai, usko hatane ke liye
        raw_text = response.text.strip().removeprefix('```json').removesuffix('```').strip()
        
        # String ko wapas JSON dictionary me convert karna
        action_json = json.loads(raw_text)
        
        return {
            "status": "success",
            "data": action_json
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
