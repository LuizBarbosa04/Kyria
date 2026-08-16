TERMOS_ATUAIS = [
    "atualmente",
    "hoje",
    "agora",
    "último",
    "última",
    "atual",
    "preço",
    "cotação",
    "população",
    "presidente",
    "governador",
    "prefeito",
    "ministro",
    "versão",
    "notícia",
    "notícias",
    "temperatura",
    "clima",
    "eleição",
    "lei",
    "salário",
    "valor",
    "mercado"
]


def precisa_verificacao(pergunta):
    pergunta = pergunta.lower()

    for termo in TERMOS_ATUAIS:
        if termo in pergunta:
            return True

    return False