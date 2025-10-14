#!/usr/bin/env pwsh

<#
.SYNOPSIS
    Development dashboard for Reserve Flow AI 2026
.DESCRIPTION
    Provides real-time status of development environment, services,
    test results, and development metrics.
#>

param(
    [switch]$Watch,
    [int]$Interval = 30
)

# Configuration
$BACKEND_PORT = 8000
$FRONTEND_PORT = 5173
$BACKEND_URL = "http://localhost:$BACKEND_PORT"
$FRONTEND_URL = "http://localhost:$FRONTEND_PORT"

# Colors
$Green = "Green"
$Yellow = "Yellow"
$Red = "Red"
$Cyan = "Cyan"
$White = "White"
$Magenta = "Magenta"

function Write-ColorOutput {
    param([string]$Message, [string]$Color = $White)
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

function Test-HealthEndpoint {
    param([string]$Url)
    try {
        $response = Invoke-WebRequest -Uri "$Url/health" -TimeoutSec 3 -ErrorAction Stop
        return $response.StatusCode -eq 200
    }
    catch {
        return $false
    }
}

function Get-GitStatus {
    try {
        $status = git status --porcelain 2>$null
        $lines = $status | Measure-Object -Line
        return @{
            Modified = ($status | Where-Object { $_ -match "^ M" }).Count
            Added = ($status | Where-Object { $_ -match "^A" }).Count
            Deleted = ($status | Where-Object { $_ -match "^D" }).Count
            Untracked = ($status | Where-Object { $_ -match "^??" }).Count
            Total = $lines.Count
        }
    }
    catch {
        return @{ Modified = 0; Added = 0; Deleted = 0; Untracked = 0; Total = 0 }
    }
}

function Get-TestStatus {
    $status = @{
        Backend = @{ Passed = 0; Failed = 0; Total = 0 }
        Frontend = @{ Passed = 0; Failed = 0; Total = 0 }
    }

    # Backend tests
    if (Test-Path "backend/tests") {
        try {
            Push-Location backend
            & ".\venv\Scripts\activate.ps1"
            $result = pytest --tb=no -q 2>$null
            $status.Backend.Total = ($result | Select-String "passed|failed" | Measure-Object).Count
            $status.Backend.Passed = ($result | Select-String "passed" | Measure-Object).Count
            $status.Backend.Failed = ($result | Select-String "failed" | Measure-Object).Count
            Pop-Location
        }
        catch {
            $status.Backend = @{ Passed = 0; Failed = 0; Total = 0 }
        }
    }

    # Frontend tests
    if (Test-Path "frontend") {
        try {
            Push-Location frontend
            $result = npm test -- --run --reporter=json 2>$null | ConvertFrom-Json
            if ($result) {
                $status.Frontend.Total = $result.numTotalTests
                $status.Frontend.Passed = $result.numPassedTests
                $status.Frontend.Failed = $result.numFailedTests
            }
            Pop-Location
        }
        catch {
            $status.Frontend = @{ Passed = 0; Failed = 0; Total = 0 }
        }
    }

    return $status
}

function Get-SystemInfo {
    $cpu = Get-WmiObject Win32_Processor | Select-Object -First 1
    $memory = Get-WmiObject Win32_OperatingSystem

    return @{
        CPU = "{0}%" -f [math]::Round($cpu.LoadPercentage, 1)
        Memory = "{0} MB free / {1} MB total" -f [math]::Round($memory.FreePhysicalMemory / 1KB, 0), [math]::Round($memory.TotalVisibleMemorySize / 1KB, 0)
        Disk = Get-WmiObject Win32_LogicalDisk -Filter "DeviceID='C:'" | ForEach-Object {
            "{0} GB free / {1} GB total" -f [math]::Round($_.FreeSpace / 1GB, 1), [math]::Round($_.Size / 1GB, 1)
        }
    }
}

function Show-Dashboard {
    Clear-Host

    $dateTime = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    Write-ColorOutput "🚀 Reserve Flow AI 2026 - Development Dashboard" $Cyan
    Write-ColorOutput "=" * 60 $Cyan
    Write-ColorOutput "📅 $dateTime" $White
    Write-ColorOutput ""

    # Service Status
    Write-ColorOutput "🔧 Service Status" $Yellow
    Write-ColorOutput "-" * 20 $White

    $backendStatus = if (Test-Port -Port $BACKEND_PORT) {
        if (Test-HealthEndpoint -Url $BACKEND_URL) { "✅ Running (Healthy)" } else { "⚠️  Running (Unhealthy)" }
    } else { "❌ Stopped" }

    $frontendStatus = if (Test-Port -Port $FRONTEND_PORT) { "✅ Running" } else { "❌ Stopped" }

    Write-ColorOutput ("Backend (:{0}):  {1}" -f $BACKEND_PORT, $backendStatus) $White
    Write-ColorOutput ("Frontend (:{0}): {1}" -f $FRONTEND_PORT, $frontendStatus) $White
    Write-ColorOutput ""

    # URLs
    Write-ColorOutput "🔗 Quick Links" $Yellow
    Write-ColorOutput "-" * 20 $White
    Write-ColorOutput "📱 Frontend:    $FRONTEND_URL" $White
    Write-ColorOutput "🔧 Backend:     $BACKEND_URL" $White
    Write-ColorOutput "📚 API Docs:    $BACKEND_URL/docs" $White
    Write-ColorOutput "🔍 Health:      $BACKEND_URL/health" $White
    Write-ColorOutput ""

    # Git Status
    $gitStatus = Get-GitStatus
    Write-ColorOutput "📋 Git Status" $Yellow
    Write-ColorOutput "-" * 20 $White
    Write-ColorOutput ("Modified:  {0}" -f $gitStatus.Modified) $White
    Write-ColorOutput ("Added:     {0}" -f $gitStatus.Added) $White
    Write-ColorOutput ("Deleted:   {0}" -f $gitStatus.Deleted) $White
    Write-ColorOutput ("Untracked: {0}" -f $gitStatus.Untracked) $White
    Write-ColorOutput ("Total:     {0}" -f $gitStatus.Total) $White
    Write-ColorOutput ""

    # Test Status
    $testStatus = Get-TestStatus
    Write-ColorOutput "🧪 Test Status" $Yellow
    Write-ColorOutput "-" * 20 $White
    Write-ColorOutput ("Backend:  {0} passed, {1} failed ({2} total)" -f $testStatus.Backend.Passed, $testStatus.Backend.Failed, $testStatus.Backend.Total) $White
    Write-ColorOutput ("Frontend: {0} passed, {1} failed ({2} total)" -f $testStatus.Frontend.Passed, $testStatus.Frontend.Failed, $testStatus.Frontend.Total) $White
    Write-ColorOutput ""

    # System Resources
    $systemInfo = Get-SystemInfo
    Write-ColorOutput "💻 System Resources" $Yellow
    Write-ColorOutput "-" * 20 $White
    Write-ColorOutput ("CPU:    {0}" -f $systemInfo.CPU) $White
    Write-ColorOutput ("Memory: {0}" -f $systemInfo.Memory) $White
    Write-ColorOutput ("Disk:   {0}" -f $systemInfo.Disk) $White
    Write-ColorOutput ""

    # Recent Activity
    Write-ColorOutput "📈 Recent Activity" $Yellow
    Write-ColorOutput "-" * 20 $White

    # Show recent git commits
    try {
        $recentCommits = git log --oneline -5 2>$null
        if ($recentCommits) {
            $recentCommits | ForEach-Object { Write-ColorOutput "  $_" $White }
        } else {
            Write-ColorOutput "  No recent commits" $White
        }
    }
    catch {
        Write-ColorOutput "  Git not available" $White
    }

    Write-ColorOutput ""
    Write-ColorOutput "=" * 60 $Cyan

    if ($Watch) {
        Write-ColorOutput "🔄 Refreshing every $Interval seconds... (Ctrl+C to stop)" $Magenta
    }
}

# Main execution
if ($Watch) {
    Write-ColorOutput "🔄 Starting dashboard in watch mode (Ctrl+C to stop)" $Magenta
    while ($true) {
        Show-Dashboard
        Start-Sleep -Seconds $Interval
    }
} else {
    Show-Dashboard
}
