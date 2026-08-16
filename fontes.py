import os

import requests
from dotenv import load_dotenv

load_dotenv()

TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")


def pesquisar_fontes(pergunta):
    if not TAVILY_API_KEY:
        return []

    try:
        resposta = requests.post(
            "https://api.tavily.com/search",
            headers={
                "Authorization": f"Bearer {TAVILY_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "query": pergunta,
                "search_depth": "basic",
                "max_results": 3,
                "include_answer": False,
                "include_raw_content": False
            },
            timeout=15
        )

        resposta.raise_for_status()

        dados = resposta.json()

        return dados.get("results", [])

    except requests.RequestException:
        return []