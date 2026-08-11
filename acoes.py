from datetime import datetime
from urllib.parse import quote_plus
import subprocess
import webbrowser

programas = {
    "bloco de notas": "notepad.exe",
    "calculadora": "calc.exe"
}

sites = {
    "youtube": "https://www.youtube.com"
}

def mostrar_hora(falar):
    agora = datetime.now()
    hora = agora.strftime("%H:%M")
    resposta = f"Agora são {hora}."
    print(resposta)
    falar(resposta)

def mostrar_data(falar):
    agora = datetime.now()
    data = agora.strftime("%d/%m/%Y")
    resposta = f"Hoje é {data}."
    print(resposta)
    falar(resposta)

def pesquisar(pesquisa, falar):
    falar(f"Pesquisando {pesquisa}.")
    termo = quote_plus(pesquisa)
    webbrowser.open(f"https://www.google.com/search?q={termo}")

def abrir_programa(nome, falar):
    falar(f"Abrindo {nome}.")
    subprocess.Popen(programas[nome])

def abrir_site(nome, falar):
    falar(f"Abrindo {nome}.")
    webbrowser.open(sites[nome])