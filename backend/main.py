import os
from pathlib import Path
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import httpx

# ── load .env from the project root ───────────────────────────────────────────
ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / "api.env")

API_KEY      = os.getenv("API_KEY", "")
GROQ_API_URL = os.getenv("GROQ_API_URL", "https://api.groq.com/openai/v1/chat/completions")

# ── load MCJB knowledge base ──────────────────────────────────────────────────
KB_FILE = ROOT / "informacoes_mcjb.txt"

def load_knowledge_base() -> str:
    return KB_FILE.read_text(encoding="utf-8") if KB_FILE.exists() else ""


def build_system_prompt() -> str:
    knowledge_base = load_knowledge_base()
    return f"""
Você é a assistente virtual oficial do MCJB (Movimento Comunitário do Jardim Botânico).
Seja prestativa, educada, clara e objetiva. 
Use APENAS as informações da base de conhecimentos abaixo para responder.
Se a informação não estiver na base, diga educadamente que não possui essa informação e 
ofereça o contato da recepção.

<base_de_conhecimentos>
{knowledge_base}
</base_de_conhecimentos>
"""

app = FastAPI(title="MCJB Chatbot API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: List[Message]

@app.get("/health")
def health():
    return {"status": "ok", "model": "llama-3.1-8b-instant"}

@app.post("/chat")
async def chat(req: ChatRequest):
    if not API_KEY:
        raise HTTPException(status_code=500, detail="API_KEY não configurada.")

    payload = {
        "model": "llama-3.1-8b-instant",
        "messages": [
            {"role": "system", "content": build_system_prompt()},
            *[m.dict() for m in req.messages],
        ],
        "temperature": 0.4,
        "max_tokens": 1024,
    }

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
    }

    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(GROQ_API_URL, json=payload, headers=headers)

    if resp.status_code != 200:
        raise HTTPException(status_code=resp.status_code, detail=resp.text)

    data = resp.json()
    reply = data["choices"][0]["message"]["content"]
    return {"reply": reply}
