import os
import json
from fastapi import FastAPI
from pydantic import BaseModel
from dotenv import load_dotenv
from groq import Groq

# Load environment variables
load_dotenv()

app = FastAPI(title="NOVA Custom AI Server")

# Initialize Groq Client
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
# Hum try/except ya if condition laga rahe hain taaki key na hone par app crash na ho
if GROQ_API_KEY:
    client = Groq(api_key=GROQ_API_KEY)
else:
    client = None
    print("Warning: GROQ_API_KEY is not set!")

# 🧠 Aapka Custom Brain Load Karne ka function
def load_custom_brain():
    try:
        # utf-8 set kiya hai taaki Hindi/Hinglish characters aaram se padh sake
        with open("brain.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print("Brain file not found or empty:", e)
        return {}

# Server start hote hi brain memory me load ho jayega
custom_brain = load_custom_brain()

class CommandRequest(BaseModel):
    command: str

@app.get("/")
def home():
    return {"status": "NOVA Custom AI Server is Running ⚡"}

@app.post("/api/command")
async def process_command(req: CommandRequest):
    # User ki aawaz ko chote aksharon me badalna taaki match karne me aasaani ho
    user_input = req.command.lower().strip()

    # ==========================================
    # STEP 1: CHECK CUSTOM BRAIN (100% Free & Instant)
    # ==========================================
    for key_phrase, action_data in custom_brain.items():
        if key_phrase in user_input:
            print(f"Matched in Custom Brain: {key_phrase}")
            return {
                "status": "success", 
                "source": "custom_brain", 
                "data": action_data
            }

    # ==========================================
    # STEP 2: FALLBACK TO GROQ AI (Fast Llama 3 Model)
    # ==========================================
    if not client:
         return {
             "status": "error", 
             "data": {"action": "speak", "text": "Groq API key server par set nahi hai bhai."}
         }

    system_prompt = """
    You are NOVA, a smart Android Assistant. User command: "{}"
    Return ONLY a valid JSON object. No other text.
    Actions allowed: 
    1. {"action": "open_system_app", "app_name": "appname"}
    2. {"action": "search_youtube", "query": "search query"}
    3. {"action": "speak", "text": "Your natural conversational answer in Hinglish"}
    """
    
    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": system_prompt.format(req.command)
                }
            ],
            model="llama3-8b-8192", # Groq ka sabse fast model
            temperature=0.3,
            max_tokens=150
        )
        
        response_text = chat_completion.choices[0].message.content.strip()
        
        # AI kabhi kabhi JSON ke bahar ``` daal deta hai, usko clean karna
        response_text = response_text.replace('```json', '').replace('```', '').strip()
        
        action_json = json.loads(response_text)
        return {"status": "success", "source": "groq_ai", "data": action_json}

    except Exception as e:
        print("Groq Error:", e)
        return {
            "status": "error", 
            "data": {"action": "speak", "text": "Internet ya server me thoda issue chal raha hai."}
        }
