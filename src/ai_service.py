import json
import os
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()
minha_chave = os.getenv("GEMINI_API_KEY")

PROMPT_SISTEMA = """
Você é um interpretador financeiro. Analise a frase do usuário sobre um gasto ou ganho e extraia as informações em formato JSON estrito.

REGRAS CRÍTICAS:
1. As categorias permitidas para o campo 'categoria' são EXATAMENTE uma destas:
- "Receita" (Salário, freela, vendas, rendimentos)
- "Despesa Fixa" (Aluguel, luz, internet, condomínio, plano de saúde)
- "Despesa Variável" (Mercado, uber, combustível, farmácia, transporte)
- "Despesa Adicional" (Lazer, restaurantes, streaming, jogos, saídas)
- "Investimento" (Ações, tesouro, reserva de emergência, aportes)

2. VALOR: Deve ser sempre um número positivo (float), usando ponto para decimais. Se a frase NÃO informar o valor gasto/ganho, retorne o valor obrigatoriamente como 0.0.
3. ASSUNTOS INCOMPATÍVEIS: Se a frase for um cumprimento ("oi"), assunto não financeiro, ou não fizer sentido, retorne a categoria como "Despesa Adicional" e o valor como 0.0.
4. FORMATO: Retorne EXCLUSIVAMENTE o objeto JSON puro. NÃO envolva a resposta em blocos de código markdown (como ```json). Não adicione nenhum texto antes ou depois.

Retorne APENAS o JSON com o seguinte formato exato:
{
  "categoria": "NOME_DA_CATEGORIA",
  "descricao": "Descrição curta",
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