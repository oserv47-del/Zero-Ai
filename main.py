import os
import json
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

app = FastAPI(title="NOVA Custom AI Server")

# Initialize Fast Groq Client (Llama 3)
GROQ_API_KEY = os.getenv("gsk_76biwXFmSIC5Ihpzm9sxWGdyb3FY6doAIVZO9pVya3Agn0XSS6S3n")
client = Groq(api_key=GROQ_API_KEY)

# Load your Custom Trained Data
def load_brain():
    try:
        with open("brain.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

custom_brain = load_brain()

class CommandRequest(BaseModel):
    command: str

@app.get("/")
def home():
    return {"status": "NOVA Custom Brain is Live and FAST! ⚡"}

@app.post("/api/command")
async def process_command(req: CommandRequest):
    user_input = req.command.lower()

    # ==========================================
    # STEP 1: CHECK CUSTOM TRAINED BRAIN (0 Latency)
    # ==========================================
    for key_phrase, action_data in custom_brain.items():
        if key_phrase in user_input:
            # Agar trained data match ho gaya, to turant fast reply karo
            return {"status": "success", "source": "custom_brain", "data": action_data}


    # ==========================================
    # STEP 2: FALLBACK TO FAST AI (Groq - Llama 3)
    # ==========================================
    system_prompt = """
    You are an advanced Android Assistant. User command: "{}"
    Return ONLY valid JSON.
    Actions allowed: open_system_app (app_name), search_youtube (query), speak (text).
    """
    
    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": system_prompt.format(req.command)
                }
            ],
            model="llama3-8b-8192", # Extremely fast model
            temperature=0.3,
            max_tokens=100
        )
        
        response_text = chat_completion.choices[0].message.content.strip()
        
        # Parse JSON
        action_json = json.loads(response_text)
        return {"status": "success", "source": "llama3_ai", "data": action_json}

    except Exception as e:
        print("AI Error:", e)
        # Agar net/API issue ho, toh error bolne ko kaho
        return {
            "status": "error", 
            "data": {"action": "speak", "text": "Bhai, network ya server me kuch issue hai."}
        }
