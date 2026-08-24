import json
import os
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()
minha_chave = os.getenv("GEMINI_API_KEY")

PROMPT_SISTEMA = """
Você é um interpretador financeiro. Analise a frase do usuário sobre um gasto ou ganho e extraia as informações em formato JSON estrito.

As categorias permitidas para o campo 'categoria' são EXATAMENTE uma destas:
- "Receita" (Salário, freela, vendas, rendimentos)
- "Despesa Fixa" (Aluguel, luz, internet, condomínio, plano de saúde)
- "Despesa Variável" (Mercado, uber, combustível, farmácia, transporte)
- "Despesa Adicional" (Lazer, restaurantes, streaming, jogos, saídas)
- "Investimento" (Ações, tesouro, reserva de emergência, aportes)

Retorne APENAS o JSON com o seguinte formato exato:
{
  "categoria": "NOME_DA_CATEGORIA",
  "descricao": "Descrição curta do item",
  "valor": 0.0
}
"""

def interpretar_transacao(texto: str) -> dict:
    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    
    if not api_key:
        raise ValueError("Chave de API não encontrada! Configure a variável GEMINI_API_KEY ou GOOGLE_API_KEY.")

    client = genai.Client(api_key=api_key)

    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=f"{PROMPT_SISTEMA}\n\nFrase a ser interpretada: '{texto}'",
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            temperature=0.1
        ),
    )

    return json.loads(response.text)