from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Gizmo Gateway")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/healthz")
def health():
    return {"status": "ok"}

@app.get("/")
def root():
    return {"status": "ok"}

@app.get("/parse")
def parse_get(text: str | None = None, q: str | None = None):
    msg = text or q
    return {"reply": f"echo: {msg}"} if msg else {"reply": "unknown (no query param)"}

@app.post("/parse")
async def parse_post(request: Request):
    try:
        data = await request.json()
    except Exception:
        data = {}
    msg = (
        (isinstance(data, str) and data)
        or data.get("command")
        or data.get("prompt")
        or data.get("message")
        or data.get("text")
    )
    if not msg:
        return {"reply": "unknown", "received": data}
    return {"reply": f"echo: {msg}"}
