$ErrorActionPreference = "Stop"

$porta = 8000
$endereco = "http://127.0.0.1:$porta"
$pythonKyria = Join-Path $PSScriptRoot ".venv\Scripts\python.exe"

function Testar-Api {
    try {
        $resposta = Invoke-WebRequest -Uri $endereco -TimeoutSec 1
        return $resposta.StatusCode -eq 200
    }
    catch {
        return $false
    }
}

if (-not (Test-Path $pythonKyria)) {
    Write-Error "Não encontrei o Python da .venv em $pythonKyria"
    exit 1
}

if (-not (Testar-Api)) {
    $argumentos = "-m uvicorn api:app --host 127.0.0.1 --port $porta"

    Start-Process `
        -FilePath $pythonKyria `
        -ArgumentList $argumentos `
        -WorkingDirectory $PSScriptRoot `
        -WindowStyle Hidden

    for ($tentativa = 1; $tentativa -le 20; $tentativa++) {
        Start-Sleep -Milliseconds 500

        if (Testar-Api) {
            Start-Process $endereco
            exit 0
        }
    }

    Write-Error "A API do Kyria não respondeu em 10 segundos."
    exit 1
}

Start-Process $endereco
