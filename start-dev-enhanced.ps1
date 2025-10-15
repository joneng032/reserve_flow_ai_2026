#!/usr/bin/env pwsh

<#
.SYNOPSIS
    Enhanced development launcher for Reserve Flow AI 2026
.DESCRIPTION
    Automates development environment setup, dependency installation,
    environment validation, and parallel service startup with health checks.
#>

param(
    [switch]$SkipDeps,
    [switch]$SkipValidation,
    [switch]$Clean
)

# Configuration
$BACKEND_PORT = 3000
$FRONTEND_PORT = 5173
$BACKEND_URL = "http://localhost:$BACKEND_PORT"
$FRONTEND_URL = "http://localhost:$FRONTEND_PORT"

# Colors for output
$Green = "Green"
$Yellow = "Yellow"
$Red = "Red"
$Cyan = "Cyan"

function Write-ColorOutput {
    param([string]$Message, [string]$Color = "White")
    Write-Host $Message -ForegroundColor $Color
}

function Test-Port {
    param([int]$Port)
    try {
        $connection = New-Object System.Net.Sockets.TcpClient
        $connection.Connect("localhost", $Port)
        $connection.Close()
        return $true
    }
    catch {
        return $false
    }
}

function Wait-ForService {
    param([int]$Port, [string]$ServiceName, [int]$TimeoutSeconds = 60)
    Write-ColorOutput "⏳ Waiting for $ServiceName on port $Port..." $Yellow

    $startTime = Get-Date
    while (((Get-Date) - $startTime).TotalSeconds -lt $TimeoutSeconds) {
        if (Test-Port -Port $Port) {
            Write-ColorOutput "✅ $ServiceName is ready on port $Port" $Green
            return $true
        }
        Start-Sleep -Seconds 2
    }

    Write-ColorOutput "❌ $ServiceName failed to start within ${TimeoutSeconds}s" $Red
    return $false
}

function Test-HealthEndpoint {
    param([string]$Url, [string]$ServiceName)
    try {
        $response = Invoke-WebRequest -Uri "$Url/health" -TimeoutSec 5 -ErrorAction Stop
        if ($response.StatusCode -eq 200) {
            Write-ColorOutput "✅ $ServiceName health check passed" $Green
            return $true
        }
    }
    catch {
        Write-ColorOutput "⚠️  $ServiceName health check failed (endpoint may not exist)" $Yellow
        return $false
    }
    return $false
}

function Install-BackendDependencies {
    Write-ColorOutput "📦 Installing backend dependencies..." $Cyan

    if (!(Test-Path "backend")) {
        Write-ColorOutput "❌ Backend directory not found" $Red
        return $false
    }

    Push-Location backend

    # Check if virtual environment exists
    if (!(Test-Path "venv")) {
        Write-ColorOutput "🐍 Creating Python virtual environment..." $Cyan
        python -m venv venv
    }

    # Activate virtual environment and install dependencies
    & ".\venv\Scripts\activate.ps1"
    python -m pip install --upgrade pip
    pip install -r requirements.txt

    Pop-Location
    return $true
}

function Install-FrontendDependencies {
    Write-ColorOutput "📦 Installing frontend dependencies..." $Cyan

    if (!(Test-Path "frontend")) {
        Write-ColorOutput "❌ Frontend directory not found" $Red
        return $false
    }

    Push-Location frontend

    if (!(Test-Path "node_modules")) {
        Write-ColorOutput "📦 Installing Node.js dependencies..." $Cyan
        npm install
    } else {
        Write-ColorOutput "📦 Node.js dependencies already installed" $Green
    }

    Pop-Location
    return $true
}

function Validate-Environment {
    Write-ColorOutput "🔍 Validating development environment..." $Cyan

    $issues = @()

    # Check Python
    try {
        $pythonVersion = python --version 2>$null
        Write-ColorOutput "✅ Python: $pythonVersion" $Green
    }
    catch {
        $issues += "Python is not installed or not in PATH"
    }

    # Check Node.js
    try {
        $nodeVersion = node --version 2>$null
        Write-ColorOutput "✅ Node.js: $nodeVersion" $Green
    }
    catch {
        $issues += "Node.js is not installed or not in PATH"
    }

    # Check npm
    try {
        $npmVersion = npm --version 2>$null
        Write-ColorOutput "✅ npm: $npmVersion" $Green
    }
    catch {
        $issues += "npm is not installed or not in PATH"
    }

    # Check required files
    $requiredFiles = @(
        "backend/requirements.txt",
        "frontend/package.json",
        "backend/main.py",
        "frontend/src/main.tsx"
    )

    foreach ($file in $requiredFiles) {
        if (!(Test-Path $file)) {
            $issues += "Required file missing: $file"
        }
    }

    if ($issues.Count -gt 0) {
        Write-ColorOutput "❌ Environment validation failed:" $Red
        foreach ($issue in $issues) {
            Write-ColorOutput "   - $issue" $Red
        }
        return $false
    }

    Write-ColorOutput "✅ Environment validation passed" $Green
    return $true
}

function Clean-Environment {
    Write-ColorOutput "🧹 Cleaning development environment..." $Cyan

    # Remove Python cache
    Get-ChildItem -Path "." -Recurse -Directory -Name "__pycache__" | ForEach-Object {
        Remove-Item -Path $_ -Recurse -Force -ErrorAction SilentlyContinue
    }

    # Remove node_modules (optional, ask user)
    if (Test-Path "frontend/node_modules") {
        $response = Read-Host "Remove frontend/node_modules? (y/N)"
        if ($response -eq "y" -or $response -eq "Y") {
            Remove-Item "frontend/node_modules" -Recurse -Force
            Write-ColorOutput "🗑️  Removed frontend/node_modules" $Yellow
        }
    }

    Write-ColorOutput "✅ Environment cleaned" $Green
}

function Show-DevDashboard {
    Write-Host "`n🚀 Reserve Flow AI 2026 - Development Environment" -ForegroundColor $Cyan
    Write-Host "=" * 50 -ForegroundColor $Cyan
    Write-Host "📱 Frontend: $FRONTEND_URL" -ForegroundColor White
    Write-Host "🔧 Backend:  $BACKEND_URL" -ForegroundColor White
    Write-Host "📚 API Docs: $BACKEND_URL/docs" -ForegroundColor White
    Write-Host "🔍 Health:   $BACKEND_URL/health" -ForegroundColor White
    Write-Host "=" * 50 -ForegroundColor $Cyan
    Write-Host "💡 Tips:" -ForegroundColor $Yellow
    Write-Host "   - Use Ctrl+C to stop all services" -ForegroundColor White
    Write-Host "   - Check logs in separate terminal windows" -ForegroundColor White
    Write-Host "   - Frontend hot-reloads automatically" -ForegroundColor White
    Write-Host "   - Backend requires restart for code changes" -ForegroundColor White
    Write-Host "=" * 50 -ForegroundColor $Cyan
}

# Main execution
Write-ColorOutput "🚀 Starting Reserve Flow AI 2026 Development Environment" $Green
Write-ColorOutput "Press Ctrl+C to stop all services`n" $Yellow

# Clean if requested
if ($Clean) {
    Clean-Environment
}

# Validate environment
if (!$SkipValidation) {
    if (!(Validate-Environment)) {
        Write-ColorOutput "❌ Environment validation failed. Please fix issues and try again." $Red
        exit 1
    }
}

# Install dependencies
if (!$SkipDeps) {
    if (!(Install-BackendDependencies)) {
        Write-ColorOutput "❌ Backend dependency installation failed" $Red
        exit 1
    }

    if (!(Install-FrontendDependencies)) {
        Write-ColorOutput "❌ Frontend dependency installation failed" $Red
        exit 1
    }
}

# Check if services are already running
$backendRunning = Test-Port -Port $BACKEND_PORT
$frontendRunning = Test-Port -Port $FRONTEND_PORT

if ($backendRunning -and $frontendRunning) {
    Write-ColorOutput "✅ All services are already running!" $Green
    Show-DevDashboard
    exit 0
}

# Start backend if not running
if (!$backendRunning) {
    Write-ColorOutput "🔧 Starting backend service..." $Cyan
    $backendJob = Start-Job -ScriptBlock {
        param($backendPath)
        Set-Location $backendPath
        & ".\venv\Scripts\activate.ps1"
        python main.py
    } -ArgumentList (Join-Path $PSScriptRoot "backend")

    # Wait a moment for backend to start
    Start-Sleep -Seconds 3

    # Check if backend started successfully
    if (!(Wait-ForService -Port $BACKEND_PORT -ServiceName "Backend")) {
        Write-ColorOutput "❌ Backend failed to start" $Red
        Get-Job | Stop-Job
        Get-Job | Remove-Job
        exit 1
    }

    # Test health endpoint
    Test-HealthEndpoint -Url $BACKEND_URL -ServiceName "Backend"
}

# Start frontend if not running
if (!$frontendRunning) {
    Write-ColorOutput "🎨 Starting frontend service..." $Cyan
    $frontendJob = Start-Job -ScriptBlock {
        param($frontendPath)
        Set-Location $frontendPath
        npm run dev
    } -ArgumentList (Join-Path $PSScriptRoot "frontend")

    # Wait for frontend to start
    if (!(Wait-ForService -Port $FRONTEND_PORT -ServiceName "Frontend")) {
        Write-ColorOutput "❌ Frontend failed to start" $Red
        Get-Job | Stop-Job
        Get-Job | Remove-Job
        exit 1
    }
}

# Show dashboard
Show-DevDashboard

# Keep script running and handle Ctrl+C
try {
    while ($true) {
        Start-Sleep -Seconds 1

        # Check if services are still running
        if (!(Test-Port -Port $BACKEND_PORT)) {
            Write-ColorOutput "❌ Backend service stopped unexpectedly" $Red
            break
        }

        if (!(Test-Port -Port $FRONTEND_PORT)) {
            Write-ColorOutput "❌ Frontend service stopped unexpectedly" $Red
            break
        }
    }
}
finally {
    Write-ColorOutput "`n🛑 Stopping all services..." $Yellow
    Get-Job | Stop-Job
    Get-Job | Remove-Job
    Write-ColorOutput "✅ All services stopped" $Green
}
