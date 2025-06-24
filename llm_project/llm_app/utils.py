from jinja2 import Template
from llm_project.settings import GROQ_API_KEY,GROQ_API_URL,GROQ_MODEL,GEMINI_API_KEY,GEMINI_API_URL,TOGETHER_API_KEY,TOGETHER_API_URL,TOGETHER_MODEL
import requests
import json

def render_prompt(template_str, row_dict):
    try:
        template = Template(template_str)
        return template.render(**row_dict)
    except Exception as e:
        return f"[ERROR: {str(e)}]"


def call_groq(prompt: str):
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": GROQ_MODEL,
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ]
    }

    try:
        response = requests.post(GROQ_API_URL, headers=headers, json=data)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        return f"[GROQ ERROR: {str(e)}]"


def call_gemini(prompt: str) -> str:
    if not GEMINI_API_KEY or not GEMINI_API_URL:
        return "[GEMINI ERROR: Missing API key or URL]"

    url = f"{GEMINI_API_URL}?key={GEMINI_API_KEY}"
    headers = {
        "Content-Type": "application/json"
    }
    data = {
        "contents": [
            {
                "parts": [
                    {
                        "text": prompt
                    }
                ]
            }
        ]
    }

    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        candidates = response.json().get("candidates", [])
        return candidates[0]["content"]["parts"][0]["text"] if candidates else "[No response]"
    except Exception as e:
        return f"[GEMINI ERROR: {str(e)}]"


def call_together(prompt: str) -> str:
    headers = {
        "Authorization": f"Bearer {TOGETHER_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": TOGETHER_MODEL,
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ]
    }

    try:
        response = requests.post(TOGETHER_API_URL, headers=headers, json=payload)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        print("Together API error:", e)
        return "Error: failed to generate response from Together"


def judge_response(context: str, prompt: str, response: str) -> dict:
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    system_message = (
        "You are a strict LLM judge.\n"
        "Rate the following response based on:\n"
        "Correctness (1-10 scale): Measuring how accurately the response answers the given prompt"
        "Faithfulness (1-10 scale): Evaluating how well the response aligns with the provided dataset information"
        "Respond ONLY with a JSON dictionary like: {\"correctness\": <int value>, \"faithfulness\": <int value>}."
    )

    user_message = f"""
Context:
{context}

Prompt:
{prompt}

Response:
{response}

Please evaluate the response based on the context and prompt above.
"""

    payload = {
        "model": GROQ_MODEL,
        "messages": [
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_message}
        ]
    }

    try:
        res = requests.post(GROQ_API_URL, headers=headers, json=payload)
        res.raise_for_status()
        content = res.json()["choices"][0]["message"]["content"].strip()

        # Clean backtick formatting if needed
        if content.startswith("```json"):
            content = content.replace("```json", "").replace("```", "").strip()
        elif content.startswith("```"):
            content = content.replace("```", "").strip()

        return json.loads(content)

    except Exception as e:
        print("Groq Judging Error:", e)
        print("Raw response:", res.text if 'res' in locals() else 'N/A')
        return {"correctness": 0, "faithfulness": 0, "error": str(e)}