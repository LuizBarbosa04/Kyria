# Kyria

Kyria é uma assistente virtual pessoal em Python, criada como projeto de aprendizado. O projeto explora arquitetura de software, APIs, modelos de linguagem locais, voz, memória, segurança, automação, Git/GitHub e redes.

Atualmente, o Kyria funciona localmente no Windows com Ollama, Qwen, Piper, SQLite e uma interface web FastAPI que também pode ser instalada como PWA.

## Recursos atuais

- Chat web com FastAPI.
- Modelo local Qwen3 8B executado pelo Ollama.
- Respostas em português brasileiro.
- Memória recente em SQLite.
- Pesquisa com Tavily para perguntas que podem depender de informações atuais.
- Validação básica de entrada e saída.
- Voz local com Piper.
- Reconhecimento de voz no modo local.
- Botão para interromper a espera ou o áudio no chat web.
- Interface instalável como PWA no Windows.

## Arquitetura

```text
Navegador ou PWA
        |
        v
      FastAPI
        |
        v
      llm.py
   /    |     \
  v     v      v
Ollama Tavily SQLite
  |
  v
Qwen3 8B

FastAPI
  |
  v
Piper
  |
  v
Áudio WAV
```

## Tecnologias

- Python 3.12
- FastAPI
- Uvicorn
- Ollama
- Qwen3 8B
- Piper TTS
- SpeechRecognition
- SQLite
- Tavily API
- PWA

## Pré-requisitos

- Windows
- Python 3.12
- Ollama instalado
- Modelo `qwen3:8b` baixado no Ollama
- Microfone, se quiser usar o modo local por voz
- Chave da Tavily, caso queira pesquisa com fontes externas

## Instalação

Clone o repositório e entre na pasta do projeto:

```powershell
git clone https://github.com/LuizBarbosa04/Kyria.git
cd Kyria
```

Crie e ative o ambiente virtual:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Instale as dependências:

```powershell
python -m pip install -r requirements.txt
```

Baixe o modelo local:

```powershell
ollama pull qwen3:8b
```

## Configuração da Tavily

Crie um arquivo chamado `.env` na raiz do projeto:

```text
TAVILY_API_KEY=sua_chave_aqui
```

O arquivo `.env` é ignorado pelo Git e não deve ser enviado ao repositório.

Sem uma chave Tavily, o chat continua funcionando, mas perguntas que exigem verificação externa não receberão fontes.

## Como executar

Inicie o Ollama, caso ele ainda não esteja em execução:

```powershell
ollama serve
```

Para desenvolvimento, inicie a API com recarregamento automático:

```powershell
python -m uvicorn api:app --reload
```

Abra no navegador:

```text
http://127.0.0.1:8000
```

Se já houver uma API usando a porta `8000`, use outra porta para desenvolvimento:

```powershell
python -m uvicorn api:app --reload --host 127.0.0.1 --port 8001
```

## Iniciador do Windows

Para iniciar o Kyria localmente sem digitar o comando do Uvicorn:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\iniciar_kyria.ps1
```

O iniciador usa a `.venv`, verifica se a API local já está disponível e abre o Kyria no navegador.

## PWA no Windows

Com a API em execução, abra o Kyria no Edge ou Chrome. O navegador pode oferecer a instalação como aplicativo.

No Edge:

```text
Menu → Aplicativos → Instalar este site como um aplicativo
```

No Chrome:

```text
Menu → Instalar Kyria
```

A PWA mantém em cache apenas arquivos públicos da interface. Conversas, respostas, memória e dados privados não entram no cache.

## Modo local por voz

Execute:

```powershell
python main.py
```

Exemplos de comandos:

```text
hora
data
pesquisar inteligência artificial
sair
```

Outras frases são enviadas ao fluxo do modelo local.

## Estrutura do projeto

| Arquivo ou pasta | Responsabilidade |
| --- | --- |
| `api.py` | Interface web, PWA, chat e geração de áudio web. |
| `llm.py` | Fluxo principal com Ollama, memória, Tavily e guardrails. |
| `memoria.py` | Banco SQLite e histórico recente. |
| `fontes.py` | Pesquisa Tavily. |
| `verificador.py` | Identificação de perguntas que precisam de verificação externa. |
| `guardrails.py` | Validação básica de entrada e saída. |
| `voz.py` | Fala e reconhecimento no modo local. |
| `main.py` | Entrada do modo local por voz. |
| `comandos.py` | Processamento de comandos locais. |
| `acoes.py` | Ações locais, como hora, data, pesquisa e abertura de programas. |
| `static/` | Manifesto, service worker e ícones da PWA. |
| `voices/` | Modelo de voz do Piper. |

## Segurança e privacidade

- A chave Tavily fica em `.env` e não deve ser enviada ao Git.
- `memoria.db` é local e ignorado pelo Git.
- A API web não expõe execução arbitrária de comandos, arquivos ou controle do sistema operacional.
- O Quick Tunnel deve ser usado apenas para testes, porque pode tornar a API acessível pela internet.
- A PWA atual é local e não possui contas de usuário nem autenticação.

## Limitações atuais

- O Kyria depende de Ollama, modelo Qwen e Piper instalados localmente.
- A instalação PWA atual é voltada ao uso local no Windows.
- Não há contas, sessões, conversas separadas por usuário ou hospedagem em nuvem.
- O botão Parar interrompe a experiência no navegador, mas não encerra imediatamente uma geração já iniciada no Ollama.
- A memória enviada ao modelo é limitada às últimas 10 mensagens.

## Próximos passos

- Finalizar o comando seguro para encerrar a API local.
- Testar os ajustes do reconhecimento de voz local.
- Planejar usuários, convites, sessões e conversas para a futura versão em nuvem.
- Preparar acesso seguro por HTTPS para Android.
