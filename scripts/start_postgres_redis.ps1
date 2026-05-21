# Start PostgreSQL + Redis for local dev (Docker Compose).
# Usage (from anywhere): powershell -ExecutionPolicy Bypass -File scripts/start_postgres_redis.ps1

$ErrorActionPreference = 'Stop'
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

function Test-DockerDaemon {
    $prev = $ErrorActionPreference
    $ErrorActionPreference = 'SilentlyContinue'
    $null = docker info 2>&1
    $ok = ($LASTEXITCODE -eq 0)
    $ErrorActionPreference = $prev
    return $ok
}

function Start-DockerDesktop {
    $candidates = @(
        'C:\Program Files\Docker\Docker\Docker Desktop.exe',
        "${env:ProgramFiles}\Docker\Docker\Docker Desktop.exe"
    )
    foreach ($exe in $candidates) {
        if (Test-Path $exe) {
            Write-Host "Starting Docker Desktop: $exe"
            Start-Process $exe
            return $true
        }
    }
    return $false
}

if (-not (Test-DockerDaemon)) {
    Write-Host 'Docker daemon is not reachable (common on Windows if Docker Desktop is not running).'
    if (Start-DockerDesktop) {
        Write-Host 'Waiting for Docker to accept connections (up to 180s)...'
        $deadline = (Get-Date).AddSeconds(180)
        while ((Get-Date) -lt $deadline) {
            if (Test-DockerDaemon) {
                break
            }
            Start-Sleep -Seconds 3
        }
    }
}

if (-not (Test-DockerDaemon)) {
    Write-Error @'
Docker is still not available.

Fix:
1. Install Docker Desktop for Windows and enable the Linux engine / WSL2 backend.
2. Open "Docker Desktop" from the Start menu; wait until it shows Docker is running.
3. Re-run:  powershell -ExecutionPolicy Bypass -File scripts/start_postgres_redis.ps1

Without Docker, install PostgreSQL and Redis yourself and set DATABASE_URL / REDIS_URL in .env (see .env.example).
'@
    exit 1
}

Write-Host "Bringing up postgres and redis in: $Root"
$ErrorActionPreference = 'SilentlyContinue'
docker compose version 2>&1 | Out-Null
$hasComposePlugin = ($LASTEXITCODE -eq 0)
$ErrorActionPreference = 'Stop'

if ($hasComposePlugin) {
    docker compose up -d postgres redis
} else {
    docker-compose up -d postgres redis
}
if ($LASTEXITCODE -ne 0) {
    exit $LASTEXITCODE
}

Write-Host @'

Next (local uvicorn + .env pointing at localhost):
  alembic upgrade head
  python scripts/seed_data.py
  uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

Default ports: PostgreSQL 5432, Redis 6379 (aligned with .env.example).
'@
