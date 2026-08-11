import requests

def perguntar_llm(pergunta):
    try:
        resposta = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "llama3.2:3b",
                "prompt": pergunta,
                "system": "Você é Kyria, uma assistente virtual. Responda sempre em português brasileiro, de forma direta e curta, usando no máximo duas frases.",
                "stream": False,
                "options": {
                    "num_predict": 80
                }
            },
            timeout=30
        )

        resposta.raise_for_status()

        dados = resposta.json()
        return dados.get("response", "").strip()

    except requests.RequestException:
        return "Não consegui acessar o modelo de inteligência artificial."