import google.generativeai as genai
from config import GEMINI_API_KEY

genai.configure(api_key=GEMINI_API_KEY)

model = genai.GenerativeModel("gemini-1.5-flash")

def write_article(topic):
    prompt = f"""
    Write a completely original sports news article about:
    {topic}

    Requirements:
    - SEO friendly title
    - 600-800 words
    - Professional journalist style
    - No plagiarism
    """

    response = model.generate_content(prompt)

    return response.text
