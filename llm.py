import requests

from memoria import criar_banco, carregar_historico, salvar_mensagem

criar_banco()


def perguntar_llm(pergunta):
    try:
        historico = carregar_historico()

        mensagens = [
            {
                "role": "system",
                "content": "Você é Kyria, uma assistente virtual. Responda sempre em português brasileiro, de forma direta e clara. Prefira respostas curtas, mas não corte informações importantes quando a pergunta exigir mais detalhes."
            }
        ]

        mensagens.extend(historico)

        mensagens.append({
            "role": "user",
            "content": pergunta
        })

        resposta = requests.post(
            "http://localhost:11434/api/chat",
            json={
                "model": "qwen3:8b",
                "messages": mensagens,
                "stream": False,
                "think": False,
                "options": {
                    "num_predict": 200
                }
            },
            timeout=30
        )

        resposta.raise_for_status()

        dados = resposta.json()

        texto = dados["message"]["content"].strip()

        salvar_mensagem("user", pergunta)
        salvar_mensagem("assistant", texto)

        return texto

    except requests.RequestException:
        return "Não consegui acessar o modelo de inteligência artificial."