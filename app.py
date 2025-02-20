# app.py
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import uvicorn

app = FastAPI()

# Armazenamento em memória dos agendamentos
agendamentos = []

# Dicionário simples de "tema" -> lista de palavras-chave
TOPIC_KEYWORDS = {
    "saúde": ["saúde", "doente", "hospital", "remédio", "exame", "posto de saúde", "doença"],
    "segurança": ["segurança", "crime", "assalto", "violência", "polícia"],
    "educação": ["educação", "escola", "professor", "aluno", "estudo", "faculdade"],
    "trabalho": ["trabalho", "emprego", "salário", "contrato", "demissão"],
    "infraestrutura": ["estrada", "asfalto", "ponte", "obra", "pavimentação"],
}

def capturar_tema_conversa(historico: str) -> str:
    """
    Faz uma análise simples do histórico, procurando por palavras-chave
    em TOPIC_KEYWORDS. Retorna o tema correspondente ou 'outros' se não achar nada.
    """
    texto_lower = historico.lower()
    for tema, keywords in TOPIC_KEYWORDS.items():
        for kw in keywords:
            if kw in texto_lower:
                return tema
    return "outros"

class WebhookBody(BaseModel):
    name: str
    history: str  # String que contém o histórico completo

@app.post("/webhook")
async def receber_webhook(body: WebhookBody):
    """
    Endpoint que recebe:
    {
      "name": "Sergio",
      "history": "Minha filha está doente, preciso de ajuda..."
    }
    Faz análise do histórico e guarda em memória para exibição no dashboard.
    """
    tema_encontrado = capturar_tema_conversa(body.history)
    agendamentos.append({
        "nome": body.name,
        "tema": tema_encontrado
    })
    return {"status": "ok", "tema": tema_encontrado}

@app.get("/dashboard", response_class=HTMLResponse)
async def exibir_dashboard():
    """
    Retorna uma página HTML (Bootstrap) listando os agendamentos
    em um layout simples e responsivo.
    """
    html_inicio = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Dashboard de Agendamentos</title>
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css">
    </head>
    <body class="bg-light">
        <div class="container py-4">
            <h1 class="mb-4">Agendamentos</h1>
            <div class="row row-cols-1 row-cols-md-3 g-4">
    """
    html_fim = """
            </div>
        </div>
    </body>
    </html>
    """

    # Monta os "cards" de agendamentos
    html_cards = ""
    for ag in agendamentos:
        nome = ag["nome"]
        tema = ag["tema"]
        card = f"""
        <div class="col">
            <div class="card mb-3 shadow-sm">
                <div class="card-body">
                    <h5 class="card-title">Nome: {nome}</h5>
                    <p class="card-text">Tema: <span class="badge bg-primary">{tema}</span></p>
                </div>
            </div>
        </div>
        """
        html_cards += card

    return html_inicio + html_cards + html_fim

if __name__ == "__main__":
    # Porta alterada para 8080
    uvicorn.run("app:app", host="0.0.0.0", port=8080, reload=True)
