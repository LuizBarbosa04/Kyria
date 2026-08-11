from acoes import (
    mostrar_hora,
    mostrar_data,
    pesquisar,
    abrir_programa,
    abrir_site,
    programas,
    sites
)
from llm import perguntar_llm

def processar_comando(comando, falar):
    comando = comando.strip().lower()

    if comando == "hora":
        mostrar_hora(falar)

    elif comando == "data":
        mostrar_data(falar)

    elif comando.startswith("pesquisar "):
        pesquisa = comando.removeprefix("pesquisar ").strip()

        if pesquisa:
            pesquisar(pesquisa, falar)

    elif comando in programas:
        abrir_programa(comando, falar)

    elif comando in sites:
        abrir_site(comando, falar)

    elif comando == "sair":
        print("Kyria encerrado.")
        falar("Kyria encerrado.")
        return False

    else:
        resposta = perguntar_llm(comando)

        if resposta:
            print(resposta)
            falar(resposta)

    return True