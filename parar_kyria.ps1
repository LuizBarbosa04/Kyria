$ErrorActionPreference = "Stop"

$porta = 8000
$endereco = "http://127.0.0.1:$porta"
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

function Testar-ProcessoKyria($processo) {
    return (
        $null -ne $processo -and
        $processo.CommandLine -match "(?:^|\s)-m\s+uvicorn\s+api:app(?:\s|$)"
    )
}

if (-not (Test-Path $arquivoPid)) {
    $conexaoKyria = Get-NetTCPConnection `
        -LocalAddress "127.0.0.1" `
        -LocalPort 8000 `
        -State Listen `
        -ErrorAction SilentlyContinue | Select-Object -First 1

    if ($null -eq $conexaoKyria) {
        Write-Host "Nenhuma API local do Kyria foi encontrada."
        exit 0
    }

    $processoKyria = Get-CimInstance `
        Win32_Process `
        -Filter "ProcessId = $($conexaoKyria.OwningProcess)"

    if (-not (Testar-ProcessoKyria $processoKyria) -or -not (Testar-Api)) {
        Write-Error "A porta 8000 não pertence à API do Kyria."
        exit 1
    }

    Stop-Process -Id $processoKyria.ProcessId -Force
    Write-Host "A API local do Kyria foi encerrada."
    exit 0
}

$textoPid = (Get-Content -LiteralPath $arquivoPid -Raw).Trim()
$pidKyria = 0

if (-not [int]::TryParse($textoPid, [ref]$pidKyria)) {
    Remove-Item -LiteralPath $arquivoPid
    Write-Error "O arquivo de identificação da API era inválido e foi removido."
    exit 1
}

$processoKyria = Get-CimInstance Win32_Process -Filter "ProcessId = $pidKyria"

if ($null -eq $processoKyria) {
    Remove-Item -LiteralPath $arquivoPid
    Write-Host "A API do Kyria já não estava em execução."
    exit 0
}

if (-not (Testar-ProcessoKyria $processoKyria) -or -not (Testar-Api)) {
    Remove-Item -LiteralPath $arquivoPid
    Write-Error "O identificador não corresponde à API do Kyria e foi removido."
    exit 1
}

Stop-Process -Id $pidKyria -Force
Remove-Item -LiteralPath $arquivoPid
Write-Host "A API local do Kyria foi encerrada."
