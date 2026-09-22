import re
import subprocess
import tempfile
from pathlib import Path
from time import perf_counter

from fastapi import FastAPI
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from starlette.background import BackgroundTask

from llm import perguntar_llm

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
MODELO_VOZ = BASE_DIR / "voices" / "pt_BR-cadu-medium.onnx"

app = FastAPI()
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


def limpar_texto(texto, remover_marcadores=False):
    texto = re.sub(r"\*\*(.*?)\*\*", r"\1", texto)
    texto = re.sub(r"\*(.*?)\*", r"\1", texto)
    texto = re.sub(r"`(.*?)`", r"\1", texto)
    texto = re.sub(r"#{1,6}\s*", "", texto)

    if remover_marcadores:
        texto = re.sub(
            r"\s*\[(Verificado com fontes externas|Não foi possível verificar|Não verificado)\]\s*",
            "",
            texto,
            flags=re.IGNORECASE
        )

    return texto.strip()


@app.get("/", response_class=HTMLResponse)
def inicio():
    return """
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <meta name="theme-color" content="#176b65">
        <title>Kyria</title>
        <link rel="manifest" href="/static/manifest.webmanifest">
        <style>
            :root {
                --fundo: #f3f0e9;
                --superficie: #fffdf8;
                --texto: #17232b;
                --texto-secundario: #5c6769;
                --borda: #cbd2cd;
                --destaque: #176b65;
                --destaque-escuro: #0f514d;
                --mensagem-kyria: #e3ebe8;
                --perigo: #a93f3f;
                --perigo-escuro: #812f2f;
                --estado-inativo: #8a9492;
                --espaco: clamp(1.25rem, 3vw, 2.5rem);
            }

            * {
                box-sizing: border-box;
            }

            body {
                min-height: 100vh;
                margin: 0;
                background: var(--fundo);
                color: var(--texto);
                font-family: "Segoe UI", sans-serif;
            }

            button,
            input {
                font: inherit;
            }

            .aplicacao {
                width: min(100%, 900px);
                min-height: 100vh;
                margin: 0 auto;
                padding: var(--espaco);
                display: grid;
                grid-template-rows: auto minmax(360px, 1fr) auto;
                gap: clamp(1rem, 2vw, 1.75rem);
            }

            .cabecalho {
                display: flex;
                justify-content: space-between;
                align-items: end;
                gap: 1rem;
                padding-bottom: 1rem;
                border-bottom: 1px solid var(--borda);
            }

            .marca {
                margin: 0;
                font-family: Georgia, serif;
                font-size: clamp(2rem, 5vw, 3.25rem);
                font-weight: 700;
                line-height: 0.9;
                letter-spacing: -0.05em;
            }

            .descricao {
                margin: 0.6rem 0 0;
                color: var(--texto-secundario);
                font-size: 0.95rem;
            }

            .estado {
                margin: 0;
                display: flex;
                align-items: center;
                gap: 0.5rem;
                color: var(--texto-secundario);
                font-size: 0.85rem;
                white-space: nowrap;
            }

            .estado::before {
                width: 0.55rem;
                height: 0.55rem;
                border-radius: 50%;
                background: var(--estado-inativo);
                content: "";
            }

            .estado[data-ativo="true"]::before {
                background: var(--destaque);
            }

            .conversa {
                min-height: 0;
                overflow-y: auto;
                padding: clamp(1rem, 3vw, 2rem);
                background: var(--superficie);
                border: 1px solid var(--borda);
            }

            .mensagens {
                min-height: 100%;
                display: flex;
                flex-direction: column;
                justify-content: end;
                gap: 1rem;
            }

            .orientacao {
                align-self: center;
                margin: auto 0;
                color: var(--texto-secundario);
                font-size: 0.95rem;
                text-align: center;
            }

            .mensagem {
                width: fit-content;
                max-width: min(78%, 620px);
                padding: 0.8rem 1rem;
                border-radius: 0.75rem;
                line-height: 1.5;
            }

            .mensagem-remetente {
                display: block;
                margin-bottom: 0.25rem;
                font-size: 0.75rem;
                font-weight: 700;
                letter-spacing: 0.04em;
                text-transform: uppercase;
            }

            .mensagem-conteudo {
                white-space: pre-wrap;
            }

            .mensagem.usuario {
                align-self: end;
                background: var(--destaque);
                color: #ffffff;
                border-bottom-right-radius: 0.15rem;
            }

            .mensagem.kyria {
                align-self: start;
                background: var(--mensagem-kyria);
                border-bottom-left-radius: 0.15rem;
            }

            .entrada {
                display: grid;
                gap: 0.75rem;
            }

            .rotulo {
                color: var(--texto-secundario);
                font-size: 0.85rem;
                font-weight: 700;
            }

            .linha-entrada {
                display: flex;
                gap: 0.65rem;
            }

            #pergunta {
                min-width: 0;
                flex: 1;
                min-height: 3rem;
                padding: 0.7rem 0.85rem;
                border: 1px solid var(--borda);
                border-radius: 0.4rem;
                background: var(--superficie);
                color: var(--texto);
            }

            #pergunta:focus,
            button:focus-visible {
                outline: 3px solid #75a7a2;
                outline-offset: 2px;
            }

            button {
                min-height: 3rem;
                padding: 0.7rem 1rem;
                border: 1px solid transparent;
                border-radius: 0.4rem;
                cursor: pointer;
                font-weight: 700;
                transition: background-color 150ms ease, border-color 150ms ease, color 150ms ease;
            }

            button:disabled {
                cursor: not-allowed;
                opacity: 0.5;
            }

            #botaoEnviar {
                background: var(--destaque);
                color: #ffffff;
            }

            #botaoEnviar:hover:not(:disabled) {
                background: var(--destaque-escuro);
            }

            #botaoMicrofone {
                background: transparent;
                border-color: var(--borda);
                color: var(--texto);
            }

            #botaoMicrofone:hover:not(:disabled) {
                border-color: var(--destaque);
                color: var(--destaque-escuro);
            }

            #botaoParar {
                background: transparent;
                border-color: var(--perigo);
                color: var(--perigo);
            }

            #botaoParar:hover:not(:disabled) {
                background: var(--perigo);
                color: #ffffff;
            }

            .aviso-erro {
                display: flex;
                justify-content: space-between;
                align-items: center;
                gap: 1rem;
                padding: 0.75rem 0.85rem;
                border-left: 3px solid var(--perigo);
                background: #f8eeee;
                color: var(--perigo-escuro);
                font-size: 0.9rem;
            }

            .aviso-erro[hidden] {
                display: none;
            }

            .aviso-erro p {
                margin: 0;
            }

            #botaoTentar {
                min-height: auto;
                padding: 0.45rem 0.65rem;
                border-color: var(--perigo);
                background: transparent;
                color: var(--perigo-escuro);
                white-space: nowrap;
            }

            #botaoTentar:hover:not(:disabled) {
                background: var(--perigo);
                color: #ffffff;
            }

            @media (max-width: 560px) {
                .aplicacao {
                    padding: 1rem;
                    gap: 1rem;
                }

                .cabecalho {
                    align-items: start;
                    flex-direction: column;
                }

                .conversa {
                    min-height: 55vh;
                    padding: 1rem;
                }

                .mensagem {
                    max-width: 88%;
                }

                .linha-entrada {
                    flex-wrap: wrap;
                }

                #pergunta {
                    flex-basis: 100%;
                }

                .linha-entrada button {
                    flex: 1;
                }

                .aviso-erro {
                    align-items: start;
                    flex-direction: column;
                }
            }
        </style>
    </head>
    <body>
        <main class="aplicacao">
            <header class="cabecalho">
                <div>
                    <h1 class="marca">Kyria</h1>
                    <p class="descricao">Assistente pessoal local</p>
                </div>
                <p id="estado" class="estado" data-ativo="false" aria-live="polite">Pronta para conversar</p>
            </header>

            <section class="conversa" aria-label="Conversa com Kyria">
                <div id="chat" class="mensagens" aria-live="polite" aria-relevant="additions">
                    <p id="orientacao" class="orientacao">Digite ou fale uma pergunta para começar.</p>
                </div>
            </section>

            <section class="entrada" aria-label="Enviar mensagem">
                <label class="rotulo" for="pergunta">Mensagem</label>
                <div class="linha-entrada">
                    <input id="pergunta" type="text" placeholder="Digite sua pergunta" autocomplete="off">
                    <button id="botaoMicrofone" type="button" onclick="ouvir()">Falar</button>
                    <button id="botaoEnviar" type="button" onclick="enviar()">Enviar</button>
                    <button id="botaoParar" type="button" onclick="parar()" disabled>Parar</button>
                </div>
                <div id="avisoErro" class="aviso-erro" role="alert" hidden>
                    <p>Não foi possível concluir a resposta. Tente novamente.</p>
                    <button id="botaoTentar" type="button" onclick="tentarNovamente()">Tentar novamente</button>
                </div>
            </section>
        </main>

        <script>
            const campo = document.getElementById("pergunta")
            const botaoEnviar = document.getElementById("botaoEnviar")
            const botaoMicrofone = document.getElementById("botaoMicrofone")
            const botaoParar = document.getElementById("botaoParar")
            const estado = document.getElementById("estado")
            const chat = document.getElementById("chat")
            const orientacao = document.getElementById("orientacao")
            const avisoErro = document.getElementById("avisoErro")
            const botaoTentar = document.getElementById("botaoTentar")

            let ocupado = false
            let controladorAtual = null
            let audioAtual = null
            let identificadorRequisicao = 0
            let ultimaPergunta = ""

            campo.addEventListener("keydown", function(evento) {
                if (evento.key === "Enter" && !ocupado) {
                    enviar()
                }
            })

            function atualizarEstado(texto, ativo) {
                estado.textContent = texto
                estado.dataset.ativo = ativo
            }

            function esconderErro() {
                avisoErro.hidden = true
            }

            function mostrarErro() {
                botaoTentar.disabled = !ultimaPergunta
                avisoErro.hidden = false
            }

            function bloquear() {
                ocupado = true
                campo.disabled = true
                botaoEnviar.disabled = true
                botaoMicrofone.disabled = true
                botaoParar.disabled = false
                atualizarEstado("Kyria está respondendo", "true")
            }

            function desbloquear() {
                ocupado = false
                campo.disabled = false
                botaoEnviar.disabled = false
                botaoMicrofone.disabled = false
                botaoParar.disabled = true
                atualizarEstado("Pronta para conversar", "false")
                campo.focus()
            }

            async function enviar(repetir = false) {
                if (ocupado) {
                    return
                }

                const pergunta = repetir ? ultimaPergunta : campo.value.trim()

                if (!pergunta) {
                    return
                }

                ultimaPergunta = pergunta
                const identificador = ++identificadorRequisicao
                controladorAtual = new AbortController()
                esconderErro()
                bloquear()

                if (!repetir) {
                    adicionarMensagem("Você", pergunta)
                }

                campo.value = ""

                try {
                    const resposta = await fetch(
                        `/perguntar?texto=${encodeURIComponent(pergunta)}`,
                        { signal: controladorAtual.signal }
                    )

                    if (!resposta.ok) {
                        throw new Error("Falha na resposta do servidor")
                    }

                    const dados = await resposta.json()

                    if (identificador !== identificadorRequisicao) {
                        return
                    }

                    controladorAtual = null
                    adicionarMensagem("Kyria", dados.resposta)
                    atualizarEstado("Kyria está falando", "true")
                    falar(dados.resposta, identificador)

                } catch (erro) {
                    if (erro.name !== "AbortError" && identificador === identificadorRequisicao) {
                        desbloquear()
                        mostrarErro()
                    }
                }
            }

            function tentarNovamente() {
                enviar(true)
            }

            function adicionarMensagem(nome, texto) {
                const mensagem = document.createElement("article")
                const remetente = document.createElement("span")
                const conteudo = document.createElement("div")

                orientacao.remove()
                mensagem.className = nome === "Você" ? "mensagem usuario" : "mensagem kyria"
                remetente.className = "mensagem-remetente"
                conteudo.className = "mensagem-conteudo"
                remetente.textContent = nome
                conteudo.textContent = texto

                mensagem.appendChild(remetente)
                mensagem.appendChild(conteudo)

                chat.appendChild(mensagem)
                chat.scrollTop = chat.scrollHeight
            }

            function falar(texto, identificador) {
                const audio = new Audio(
                    `/falar?texto=${encodeURIComponent(texto)}`
                )

                audioAtual = audio

                audio.onended = function() {
                    if (identificador === identificadorRequisicao) {
                        audioAtual = null
                        desbloquear()
                    }
                }

                audio.onerror = function() {
                    if (identificador === identificadorRequisicao) {
                        audioAtual = null
                        desbloquear()
                    }
                }

                audio.play().catch(function() {
                    if (identificador === identificadorRequisicao) {
                        audioAtual = null
                        desbloquear()
                    }
                })
            }

            function parar() {
                identificadorRequisicao += 1

                if (controladorAtual) {
                    controladorAtual.abort()
                    controladorAtual = null
                }

                if (audioAtual) {
                    audioAtual.pause()
                    audioAtual.currentTime = 0
                    audioAtual = null
                }

                desbloquear()
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

            if ("serviceWorker" in navigator) {
                window.addEventListener("load", function() {
                    navigator.serviceWorker.register("/service-worker.js")
                })
            }
        </script>
    </body>
    </html>
    """


@app.get("/service-worker.js", include_in_schema=False)
def service_worker():
    return FileResponse(
        STATIC_DIR / "service-worker.js",
        media_type="application/javascript",
        headers={"Service-Worker-Allowed": "/"}
    )


@app.get("/perguntar")
def perguntar(texto: str):
    inicio = perf_counter()

    try:
        resposta = perguntar_llm(texto)
        resposta = limpar_texto(resposta)

        return {
            "pergunta": texto,
            "resposta": resposta
        }

    finally:
        duracao = perf_counter() - inicio
        print(f"[TEMPO] /perguntar total: {duracao:.3f} s")


@app.get("/falar")
def falar(texto: str):
    inicio_total = perf_counter()
    texto = limpar_texto(texto, remover_marcadores=True)

    arquivo = tempfile.NamedTemporaryFile(
        suffix=".wav",
        delete=False
    )

    caminho_audio = Path(arquivo.name)
    arquivo.close()

    inicio_piper = perf_counter()

    try:
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

    finally:
        duracao_piper = perf_counter() - inicio_piper
        duracao_total = perf_counter() - inicio_total
        print(f"[TEMPO] Piper: {duracao_piper:.3f} s")
        print(f"[TEMPO] /falar total: {duracao_total:.3f} s")

    return FileResponse(
        caminho_audio,
        media_type="audio/wav",
        background=BackgroundTask(caminho_audio.unlink, missing_ok=True)
    )
