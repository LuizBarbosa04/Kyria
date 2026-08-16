import re
import subprocess
import tempfile
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import HTMLResponse, FileResponse

from llm import perguntar_llm

app = FastAPI()

BASE_DIR = Path(__file__).resolve().parent
MODELO_VOZ = BASE_DIR / "voices" / "pt_BR-cadu-medium.onnx"


def limpar_texto(texto):
    texto = re.sub(r"\*\*(.*?)\*\*", r"\1", texto)
    texto = re.sub(r"\*(.*?)\*", r"\1", texto)
    texto = re.sub(r"`(.*?)`", r"\1", texto)
    texto = re.sub(r"#{1,6}\s*", "", texto)

    return texto.strip()


@app.get("/", response_class=HTMLResponse)
def inicio():
    return """
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Kyria</title>
    </head>
    <body>
        <h1>Kyria</h1>

        <div id="chat"></div>

        <input id="pergunta" type="text" placeholder="Digite sua pergunta">
        <button id="botaoEnviar" onclick="enviar()">Enviar</button>
        <button id="botaoMicrofone" onclick="ouvir()">🎤</button>

        <script>
            const campo = document.getElementById("pergunta")
            const botaoEnviar = document.getElementById("botaoEnviar")
            const botaoMicrofone = document.getElementById("botaoMicrofone")

            let ocupado = false

            campo.addEventListener("keydown", function(evento) {
                if (evento.key === "Enter" && !ocupado) {
                    enviar()
                }
            })

            function bloquear() {
                ocupado = true
                campo.disabled = true
                botaoEnviar.disabled = true
                botaoMicrofone.disabled = true
            }

            function desbloquear() {
                ocupado = false
                campo.disabled = false
                botaoEnviar.disabled = false
                botaoMicrofone.disabled = false
                campo.focus()
            }

            async function enviar() {
                if (ocupado) {
                    return
                }

                const pergunta = campo.value.trim()

                if (!pergunta) {
                    return
                }

                bloquear()

                adicionarMensagem("Você", pergunta)
                campo.value = ""

                try {
                    const resposta = await fetch(
                        `/perguntar?texto=${encodeURIComponent(pergunta)}`
                    )

                    const dados = await resposta.json()

                    adicionarMensagem("Kyria", dados.resposta)
                    falar(dados.resposta)

                } catch {
                    adicionarMensagem("Kyria", "Ocorreu um erro ao processar sua mensagem.")
                    desbloquear()
                }
            }

            function adicionarMensagem(nome, texto) {
                const chat = document.getElementById("chat")
                const mensagem = document.createElement("p")

                mensagem.textContent = `${nome}: ${texto}`

                chat.appendChild(mensagem)
            }

            function falar(texto) {
                const audio = new Audio(
                    `/falar?texto=${encodeURIComponent(texto)}`
                )

                audio.onended = function() {
                    desbloquear()
                }

                audio.onerror = function() {
                    desbloquear()
                }

                audio.play().catch(function() {
                    desbloquear()
                })
            }

            function ouvir() {
                if (ocupado) {
                    return
                }

                const SpeechRecognition =
                    window.SpeechRecognition ||
                    window.webkitSpeechRecognition

                if (!SpeechRecognition) {
                    alert("Reconhecimento de voz não disponível neste navegador.")
                    return
                }

                const reconhecimento = new SpeechRecognition()

                reconhecimento.lang = "pt-BR"
                reconhecimento.interimResults = false

                reconhecimento.onresult = function(evento) {
                    const texto = evento.results[0][0].transcript

                    campo.value = texto
                    enviar()
                }

                reconhecimento.start()
            }
        </script>
    </body>
    </html>
    """


@app.get("/perguntar")
def perguntar(texto: str):
    resposta = perguntar_llm(texto)
    resposta = limpar_texto(resposta)

    return {
        "pergunta": texto,
        "resposta": resposta
    }


@app.get("/falar")
def falar(texto: str):
    texto = limpar_texto(texto)

    arquivo = tempfile.NamedTemporaryFile(
        suffix=".wav",
        delete=False
    )

    caminho_audio = Path(arquivo.name)
    arquivo.close()

    subprocess.run(
        [
            "piper",
            "--model",
            str(MODELO_VOZ),
            "--output_file",
            str(caminho_audio),
            "--length-scale",
            "0.92",
            "--noise-scale",
            "0.6",
            "--noise-w-scale",
            "0.8"
        ],
        input=texto,
        text=True,
        check=True
    )

    return FileResponse(
        caminho_audio,
        media_type="audio/wav"
    )