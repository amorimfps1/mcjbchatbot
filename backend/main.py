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

# ── MCJB knowledge base directly embedded ─────────────────────────────────────
def build_system_prompt() -> str:
    knowledge_base = """
    [INSIRA O CONTEÚDO DO ARQUIVO informacoes_mcjb.txt AQUI]
    """
    return f"""
Você é a assistente virtual oficial do MCJB (Movimento Comunitário do Jardim Botânico).
Seja prestativa, educada, clara e objetiva. 
Use APENAS as informações da base de conhecimentos abaixo para responder.
Se a informação não estiver na base, diga educadamente que não possui essa informação e 
ofereça o contato da recepção.

BASE DE CONHECIMENTOS - MCJB
Dados Institucionais

Nome: Movimento Comunitário do Jardim Botânico (MCJB)
Endereço: SHJM, Centro de Práticas Sustentáveis (CPS), Av. do Cerrado s/n, Jardins Mangueiral, Brasília-DF
Telefones: (61) 3427-3038 / (61) 99433-8517
E-mail: contato@mcjb.org.br
Site: www.mcjb.org.br
Instagram: @movimentojb
WhatsApp: https://chat.whatsapp.com/Kz1RltSaMu7LJaNacPjVhK

Horário da Recepção

Seg a Sex: 08h-12h e 14h-18h
Sábado: 08h-12h

Ecowork (Coworking)

Horário: Seg-Sex 07h30-21h | Sáb 07h30-18h
Valores avulsos: R$5/hora | R$15 (4h) | R$25 (8h)
Planos: Mensal R$169 | Semestral R$699 | Anual R$969

Associação MCJB

Mensalidade Pessoa Física: R$15/mês ou R$98/ano
Carteirinha: Preencher em https://vitrinejb.com.br/carteirinha/

Atividades e Valores (para Associados)

Yoga: Ter/Qui 19h ou Seg/Qua 08h – Trimestral a partir de R$83,24 (3x)
Pilates: Ter/Qui 09h ou 18h – Trimestral a partir de R$83,24 (2x/semana)
Tai Chi Chuan: Sáb 08h-10h
Power Jump / Bodypump: Seg/Qua/Sex pela manhã
Artes Marciais (Jiu-Jitsu, Kickboxing, Karatê, Taekwondo, Capoeira): ver horários específicos
Canto, Crochê, Tricô: Quinta e Sábado
Ballet e Ginástica Rítmica: Infantil e Teen

Matrícula

Taxa: R$25 (associado) | R$35 (não associado)
Pagamento: Cartão (recorrente) ou boleto
Aula experimental: Agendar informando nome, CPF, atividade e horário desejado

PIX e Pagamentos

PIX: 23.583.083/0001-94 (CNPJ)

Links Úteis

Site: www.mcjb.org.br
Ecowork: https://www.mcjb.org.br/ecowork/
Matrículas e atividades: www.mcjb.org.br (seção produtos)


CASO NAO SAIBA RESPONDER A PERGUNTA, ENCAMINHE PARA ALGUM MEIO DE CONTATO DO MCJB
"""

app = FastAPI(title="MCJB Chatbot API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

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
