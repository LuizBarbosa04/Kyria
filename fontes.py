import os
from time import perf_counter

import requests
from dotenv import load_dotenv

load_dotenv()

TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")


def pesquisar_fontes(pergunta):
    inicio = perf_counter()

    if not TAVILY_API_KEY:
        print("[TEMPO] Tavily: não consultada | chave não configurada")
        return []

    estado = "erro"

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
        resultados = dados.get("results", [])
        estado = f"sucesso | resultados={len(resultados)}"

        return resultados

    except requests.RequestException:
        return []

    finally:
        duracao = perf_counter() - inicio
        print(f"[TEMPO] Tavily: {duracao:.3f} s | {estado}")
