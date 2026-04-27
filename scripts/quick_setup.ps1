param(
    [switch]$NoStart,
    [switch]$SkipInstall,
    [switch]$AcceptDefaults
)

$ErrorActionPreference = "Stop"
$script:AcceptDefaults = $AcceptDefaults.IsPresent

$ProjectRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
$StartupConfigPath = Join-Path $ProjectRoot "config\startup.env"
$AppEnvPath = Join-Path $ProjectRoot ".env"
$EnvExamplePath = Join-Path $ProjectRoot ".env.example"

function Read-EnvFile {
    param([string]$Path)

    $values = [ordered]@{}
    if (-not (Test-Path -LiteralPath $Path)) {
        return $values
    }

    foreach ($line in Get-Content -LiteralPath $Path) {
        $trimmed = $line.Trim()
        if ($trimmed -eq "" -or $trimmed.StartsWith("#")) {
            continue
        }

        $parts = $trimmed.Split("=", 2)
        if ($parts.Count -eq 2) {
            $values[$parts[0]] = $parts[1]
        }
    }
    return $values
}

function Write-EnvFile {
    param(
        [string]$Path,
        [System.Collections.IDictionary]$Values,
        [string[]]$Order
    )

    $lines = @()
    foreach ($key in $Order) {
        if ($Values.Contains($key)) {
            $lines += "$key=$($Values[$key])"
        }
    }

    $directory = Split-Path -Parent $Path
    if (-not (Test-Path -LiteralPath $directory)) {
        New-Item -ItemType Directory -Path $directory | Out-Null
    }

    Set-Content -LiteralPath $Path -Value $lines -Encoding ASCII
}

function Prompt-Value {
    param(
        [string]$Label,
        [string]$Default
    )

    if ($script:AcceptDefaults) {
        return $Default
    }

    $answer = Read-Host "$Label [$Default]"
    if ([string]::IsNullOrWhiteSpace($answer)) {
        return $Default
    }
    return $answer.Trim()
}

function Prompt-YesNo {
    param(
        [string]$Label,
        [bool]$Default = $true
    )

    if ($script:AcceptDefaults) {
        return $Default
    }

    $hint = if ($Default) { "Y/n" } else { "y/N" }
    $answer = Read-Host "$Label [$hint]"
    if ([string]::IsNullOrWhiteSpace($answer)) {
        return $Default
    }
    return $answer.Trim().ToLowerInvariant().StartsWith("y")
}

function Get-ValueOrDefault {
    param(
        [System.Collections.IDictionary]$Values,
        [string]$Key,
        [string]$Default
    )

    if ($Values.Contains($Key) -and -not [string]::IsNullOrWhiteSpace($Values[$Key])) {
        return [string]$Values[$Key]
    }
    return $Default
}

function Test-CondaEnv {
    param([string]$Name)

    $json = conda env list --json | ConvertFrom-Json
    foreach ($envPath in $json.envs) {
        if ((Split-Path -Leaf $envPath) -eq $Name) {
            return $true
        }
    }
    return $false
}

function Stop-PortOwner {
    param([int]$Port)

    $connections = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue
    if (-not $connections) {
        Write-Host "[OK] Port $Port is free"
        return
    }

    $owners = $connections | Select-Object -ExpandProperty OwningProcess -Unique | Where-Object { $_ -gt 0 }
    foreach ($owner in $owners) {
        $process = Get-Process -Id $owner -ErrorAction SilentlyContinue
        $name = if ($process) { $process.ProcessName } else { "unknown" }
        if (Prompt-YesNo "Port $Port is used by PID $owner ($name). Kill it?" $true) {
            Stop-Process -Id $owner -Force -ErrorAction SilentlyContinue
            Write-Host "[OK] Killed PID $owner"
        }
    }
}

Write-Host ""
Write-Host "========================================"
Write-Host "  Task Management API Quick Setup"
Write-Host "========================================"
Write-Host "Project: $ProjectRoot"
Write-Host ""

$startup = Read-EnvFile $StartupConfigPath
$appEnv = if (Test-Path -LiteralPath $AppEnvPath) {
    Read-EnvFile $AppEnvPath
} else {
    Read-EnvFile $EnvExamplePath
}

$condaEnvName = Prompt-Value "Conda env name" (Get-ValueOrDefault $startup "CONDA_ENV_NAME" "task_demo")
$pythonVersion = Prompt-Value "Python version" (Get-ValueOrDefault $startup "PYTHON_VERSION" "3.10")
$hostName = Prompt-Value "Host" (Get-ValueOrDefault $startup "APP_HOST" "127.0.0.1")
$portText = Prompt-Value "Port" (Get-ValueOrDefault $startup "APP_PORT" "8000")
$reload = Prompt-Value "Reload true/false" (Get-ValueOrDefault $startup "APP_RELOAD" "true")
$killPort = Prompt-Value "Kill occupied port true/false" (Get-ValueOrDefault $startup "KILL_PORT_ON_START" "true")
$apiKey = Prompt-Value "API key" (Get-ValueOrDefault $appEnv "API_KEY" "dev-secret")
$channelArgs = Prompt-Value "Conda channel args" (Get-ValueOrDefault $startup "CONDA_CHANNEL_ARGS" "--override-channels -c https://repo.anaconda.com/pkgs/main")

$port = 0
if (-not [int]::TryParse($portText, [ref]$port) -or $port -lt 1 -or $port -gt 65535) {
    throw "Invalid port: $portText"
}

$startupValues = [ordered]@{
    APP_HOST = $hostName
    APP_PORT = "$port"
    APP_RELOAD = $reload
    KILL_PORT_ON_START = $killPort
    CONDA_ENV_NAME = $condaEnvName
    PYTHON_VERSION = $pythonVersion
    CONDA_CHANNEL_ARGS = $channelArgs
    UVICORN_ENV_FILE = ".env"
}

$appValues = [ordered]@{
    APP_NAME = Get-ValueOrDefault $appEnv "APP_NAME" "Task Management API"
    DATABASE_URL = Get-ValueOrDefault $appEnv "DATABASE_URL" "sqlite+aiosqlite:///./tasks.db"
    API_KEY = $apiKey
    LOG_LEVEL = Get-ValueOrDefault $appEnv "LOG_LEVEL" "INFO"
}

Write-EnvFile $StartupConfigPath $startupValues @(
    "APP_HOST",
    "APP_PORT",
    "APP_RELOAD",
    "KILL_PORT_ON_START",
    "CONDA_ENV_NAME",
    "PYTHON_VERSION",
    "CONDA_CHANNEL_ARGS",
    "UVICORN_ENV_FILE"
)
Write-EnvFile $AppEnvPath $appValues @("APP_NAME", "DATABASE_URL", "API_KEY", "LOG_LEVEL")

Write-Host "[OK] Wrote $StartupConfigPath"
Write-Host "[OK] Wrote $AppEnvPath"

if (-not (Get-Command conda -ErrorAction SilentlyContinue)) {
    throw "conda was not found in PATH. Open Anaconda Prompt or initialize conda."
}

if (-not $SkipInstall) {
    if (-not (Test-CondaEnv $condaEnvName)) {
        if (Prompt-YesNo "Create conda env '$condaEnvName' now?" $true) {
            $channelParts = $channelArgs -split "\s+" | Where-Object { $_ }
            conda create -y -n $condaEnvName "python=$pythonVersion" @channelParts
        }
    } else {
        Write-Host "[OK] Conda env exists: $condaEnvName"
    }

    conda run -n $condaEnvName python -c "import fastapi, uvicorn, sqlalchemy, aiosqlite" 2>$null
    if ($LASTEXITCODE -ne 0) {
        if (Prompt-YesNo "Install Python dependencies now?" $true) {
            conda run -n $condaEnvName python -m pip install -r (Join-Path $ProjectRoot "requirements.txt")
        }
    } else {
        Write-Host "[OK] Dependencies are installed"
    }
}

Stop-PortOwner $port

Write-Host ""
Write-Host "[OK] Quick setup complete"
Write-Host "UI:   http://${hostName}:$port/ui/"
Write-Host "Docs: http://${hostName}:$port/docs"
Write-Host "Key:  $apiKey"
Write-Host ""

if (-not $NoStart -and (Prompt-YesNo "Start server now?" $true)) {
    & (Join-Path $ProjectRoot "scripts\start.bat")
}
