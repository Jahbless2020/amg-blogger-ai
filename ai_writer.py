import google.generativeai as genai
from config import GEMINI_API_KEY

genai.configure(api_key=GEMINI_API_KEY)

model = genai.GenerativeModel("gemini-1.5-flash")

def write_article(topic):
    prompt = f"""
You are a professional sports journalist.

Write a 100% original sports article about:

{topic}

Requirements:
- Create a catchy SEO-friendly title.
- 700–900 words.
- Use headings and short paragraphs.
- Write in a natural human style.
- Do not copy from any website.
- Include a short conclusion.
- Output in HTML suitable for Blogger.
"""

    response = model.generate_content(prompt)
    return response.text
