import google.generativeai as genai
import os
from dotenv import load_dotenv

# This automatically finds and loads the .env file!
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# ... rest of the file ...
def generate_note(recipient: str, flower_id: str) -> str:
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        
        flower_name = flower_id.capitalize()
        prompt = (
            f"Write a short, warm, and poetic note (max 2 sentences) for a bouquet of {flower_name} flowers. "
            f"The recipient is '{recipient}'. Focus on the meaning of the flower. "
            "Do not use quotes or hashtags."
        )
        
        # Google recently changed their model names. 
        # This loop guarantees we find the active one for your API key.
        models_to_try = ['gemini-2.0-flash', 'gemini-1.5-flash-latest', 'gemini-1.5-pro']
        
        for model_name in models_to_try:
            try:
                model = genai.GenerativeModel(model_name)
                response = model.generate_content(prompt)
                return response.text.strip()
            except Exception as e:
                print(f"Skipping {model_name}...")
                continue
                
        # Fallback if the API completely fails
        return f"To {recipient}, hoping these {flower_id} blooms brighten your day!"
        
    except Exception as e:
        print(f"Gemini Error: {e}")
        return f"To {recipient}, hoping these {flower_id} blooms brighten your day!"