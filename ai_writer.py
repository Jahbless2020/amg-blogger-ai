import os
import google.generativeai as genai

# Prefer reading the API key from the environment; fall back to config.py if present
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    try:
        from config import GEMINI_API_KEY as CFG_KEY
        GEMINI_API_KEY = CFG_KEY
    except Exception:
        GEMINI_API_KEY = None

if not GEMINI_API_KEY:
    # Render logs will show this warning if the key is missing
    print("WARNING: GEMINI_API_KEY is not set. Generative calls will fail.")

# Configure the Gemini client
genai.configure(api_key=GEMINI_API_KEY)

# Instantiate the model (guard against errors so startup doesn't crash silently)
try:
    model = genai.GenerativeModel("gemini-1.5-flash")
except Exception as e:
    print("Warning: failed to instantiate Gemini model:", e)
    model = None


def write_article(topic):
    prompt = f"""
You are a professional sports journalist.

Write a 100% original sports article about:

{topic}

Requirements:
- Create a catchy SEO-friendly title.
- 700-900 words.
- Use headings and short paragraphs.
- Write in a natural human style.
- Do not copy from any website.
- Include a short conclusion.
- Output in HTML suitable for Blogger.
"""

    if model is None:
        return "Error: generative model not available. Check GEMINI_API_KEY and logs."

    try:
        response = model.generate_content(prompt)
    except Exception as e:
        print("Error calling model.generate_content:", e)
        return f"Error generating article: {e}"

    # Support multiple possible response shapes
    if hasattr(response, "text") and response.text:
        return response.text
    if hasattr(response, "candidates") and response.candidates:
        try:
            return response.candidates[0].content
        except Exception:
            pass
    # Fallback: stringify whole response for debugging
    return str(response)
