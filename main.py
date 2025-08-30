from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import os

# --- Optional OpenAI wiring (works if OPENAI_API_KEY is present) ---
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = None
if OPENAI_API_KEY:
    try:
        from openai import OpenAI
        client = OpenAI(api_key=OPENAI_API_KEY)
    except Exception:
        client = None

app = FastAPI(title="Gizmo Gateway")

# Allow WP to call your API (tighten this later to your domain)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check
@app.get("/")
def health():
    return {"status": "ok"}

# Simple info endpoint (optional)
@app.get("/info")
def info():
    return {
        "openai_enabled": bool(client),
        "env_vars": ["OPENAI_API_KEY" if OPENAI_API_KEY else "(none)"],
    }

# Main endpoint Gizmo calls
@app.post("/parse")
async def parse(request: Request):
    # Accept several possible key names from the WP console
    try:
        data = await request.json()
    except Exception:
        data = {}

    text = (
        (isinstance(data, str) and data)
        or data.get("command")
        or data.get("prompt")
        or data.get("message")
        or data.get("text")
    )

    if not text:
        return {"reply": "unknown", "received": data}

    # If OpenAI is configured, use it; otherwise echo
    if client:
        try:
            resp = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are Gizmo, a concise, helpful assistant."},
                    {"role": "user", "content": text},
                ],
                temperature=0.7,
            )
            return {"reply": resp.choices[0].message.content}
        except Exception as e:
            # Fall back to echo so your flow still works
            return {"reply": f"echo (fallback due to OpenAI error): {text}", "error": str(e)}

    # No OpenAI key present → echo mode
    return {"reply": f"echo: {text}"}
