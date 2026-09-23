$ErrorActionPreference = "Stop"

$porta = 8000
$endereco = "http://127.0.0.1:$porta"
$pythonKyria = Join-Path $PSScriptRoot ".venv\Scripts\python.exe"
$arquivoPid = Join-Path $PSScriptRoot ".kyria-api.pid"

function Testar-Api {
    try {
        $resposta = Invoke-WebRequest -Uri $endereco -TimeoutSec 1
        return (
            $resposta.StatusCode -eq 200 -and
            $resposta.Content -match "<title>\s*Kyria\s*</title>"
        )
    }
    catch {
        return $false
    }
}

function Obter-ProcessoDaPorta {
    $conexao = Get-NetTCPConnection `
        -LocalAddress "127.0.0.1" `
        -LocalPort $porta `
        -State Listen `
        -ErrorAction SilentlyContinue | Select-Object -First 1

    if ($null -eq $conexao) {
        return $null
    }

    return Get-CimInstance Win32_Process -Filter "ProcessId = $($conexao.OwningProcess)"
}

function Testar-ProcessoKyria($processo) {
    return (
        $null -ne $processo -and
        $processo.CommandLine -match "(?:^|\s)-m\s+uvicorn\s+api:app(?:\s|$)"
    )
}

if (-not (Test-Path $pythonKyria)) {
    Write-Error "Não encontrei o Python da .venv em $pythonKyria"
    exit 1
}

$processoDaPorta = Obter-ProcessoDaPorta

if ($null -ne $processoDaPorta) {
    if (-not (Testar-ProcessoKyria $processoDaPorta) -or -not (Testar-Api)) {
        Write-Error "A porta $porta já está sendo usada por outro programa."
        exit 1
    }

    Set-Content -LiteralPath $arquivoPid -Value $processoDaPorta.ProcessId -NoNewline
    Start-Process $endereco
    exit 0
}

if (Test-Path $arquivoPid) {
    Remove-Item -LiteralPath $arquivoPid
}

if (-not (Testar-Api)) {
    $argumentos = "-m uvicorn api:app --host 127.0.0.1 --port $porta"

    $processoKyria = Start-Process `
        -FilePath $pythonKyria `
        -ArgumentList $argumentos `
        -WorkingDirectory $PSScriptRoot `
        -WindowStyle Hidden `
        -PassThru

    for ($tentativa = 1; $tentativa -le 20; $tentativa++) {
        Start-Sleep -Milliseconds 500

        if (Testar-Api) {
            $processoDaPorta = Obter-ProcessoDaPorta

            if (Testar-ProcessoKyria $processoDaPorta) {
                Set-Content -LiteralPath $arquivoPid -Value $processoDaPorta.ProcessId -NoNewline
                Start-Process $endereco
                exit 0
            }

            break
        }
    }

    if ($null -ne (Get-Process -Id $processoKyria.Id -ErrorAction SilentlyContinue)) {
        Stop-Process -Id $processoKyria.Id -Force
    }

    Write-Error "A API do Kyria não respondeu em 10 segundos."
    exit 1
}

Start-Process $endereco
