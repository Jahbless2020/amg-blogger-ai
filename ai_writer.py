import google.generativeai as genai
from config import GEMINI_API_KEY

# Configure the Gemini client
genai.configure(api_key=GEMINI_API_KEY)

# Use the flash model (adjust if you have a different preferred model)
model = genai.GenerativeModel("gemini-1.5-flash")


def write_article(topic):
    prompt = f"""
You are a professional sports journalist.

Write a 100% original sports article about:

{topic}

Requirements:
- Create a catchy SEO-friendly title.
- 700900 words.
- Use headings and short paragraphs.
- Write in a natural human style.
- Do not copy from any website.
- Include a short conclusion.
- Output in HTML suitable for Blogger.
"""

    # Call the client and handle a couple of possible response shapes
    response = model.generate_content(prompt)
    # Common shapes: response.text OR response.candidates[0].content
    if hasattr(response, "text") and response.text:
        return response.text
    if hasattr(response, "candidates") and response.candidates:
        try:
            return response.candidates[0].content
        except Exception:
            pass
    # Fallback: stringify whole response (for debugging)
    return str(response)
