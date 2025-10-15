#!/usr/bin/env pwsh

<#
.SYNOPSIS
    Development environment setup script for Reserve Flow AI 2026
.DESCRIPTION
    Automates the setup of the complete development environment including:
    - Dependency installation
    - Pre-commit hooks setup
    - Environment validation
    - Configuration file creation
#>

param(
    [switch]$Force,
    [switch]$SkipPreCommit
)

# Colors for output
$Green = "Green"
$Yellow = "Yellow"
$Red = "Red"
$Cyan = "Cyan"
$White = "White"

function Write-ColorOutput {
    param([string]$Message, [string]$Color = "White")
    Write-Host $Message -ForegroundColor $Color
}

function Test-Command {
    param([string]$Command)
    try {
        $null = Get-Command $Command -ErrorAction Stop
        return $true
    }
    catch {
        return $false
    }
}

function Install-PythonDependencies {
    Write-ColorOutput "🐍 Setting up Python environment..." $Cyan

    if (!(Test-Command "python")) {
        Write-ColorOutput "❌ Python is not installed or not in PATH" $Red
        return $false
    }

    # Create virtual environment if it doesn't exist
    if (!(Test-Path "backend/venv") -or $Force) {
        Write-ColorOutput "📦 Creating Python virtual environment..." $Cyan
        Push-Location backend
        python -m venv venv
        Pop-Location
    }

    # Activate and install dependencies
    Write-ColorOutput "📦 Installing Python dependencies..." $Cyan
    Push-Location backend
    & ".\venv\Scripts\activate.ps1"
    python -m pip install --upgrade pip
    pip install -r requirements.txt

    # Install additional development dependencies
    pip install black isort flake8 pre-commit pytest pytest-cov

    Pop-Location
    return $true
}

function Install-NodeDependencies {
    Write-ColorOutput "📦 Setting up Node.js environment..." $Cyan

    if (!(Test-Command "node")) {
        Write-ColorOutput "❌ Node.js is not installed or not in PATH" $Red
        return $false
    }

    if (!(Test-Command "npm")) {
        Write-ColorOutput "❌ npm is not installed or not in PATH" $Red
        return $false
    }

    Push-Location frontend

    if (!(Test-Path "node_modules") -or $Force) {
        Write-ColorOutput "📦 Installing Node.js dependencies..." $Cyan
        npm install
    }

    # Install additional development dependencies
    Write-ColorOutput "📦 Installing development dependencies..." $Cyan
    npm install --save-dev prettier eslint @typescript-eslint/parser @typescript-eslint/eslint-plugin eslint-plugin-react eslint-plugin-react-hooks vitest @vitest/ui jsdom

    Pop-Location
    return $true
}

function Setup-PreCommit {
    Write-ColorOutput "🔧 Setting up pre-commit hooks..." $Cyan

    if (!(Test-Command "pre-commit")) {
        Write-ColorOutput "❌ pre-commit is not installed. Installing..." $Yellow
        pip install pre-commit
    }

    Write-ColorOutput "🔧 Installing pre-commit hooks..." $Cyan
    pre-commit install

    Write-ColorOutput "🔧 Installing pre-commit hooks for commit-msg..." $Cyan
    pre-commit install --hook-type commit-msg

    return $true
}

function Create-EnvironmentFiles {
    Write-ColorOutput "📝 Creating environment configuration files..." $Cyan

    # Backend .env
    if (!(Test-Path "backend/.env")) {
        Write-ColorOutput "📝 Creating backend/.env..." $Cyan
        @"
# Supabase Configuration
SUPABASE_URL=your-supabase-url-here
SUPABASE_ANON_KEY=your-anon-key-here
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key-here

# JWT Configuration
JWT_SECRET_KEY=your-jwt-secret-key-here
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30

# Development Settings
DEBUG=True
ENVIRONMENT=development

# CORS Settings
ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000
"@ | Out-File -FilePath "backend/.env" -Encoding UTF8
        Write-ColorOutput "✅ Created backend/.env (please update with your actual values)" $Green
    }

    # Frontend .env
    if (!(Test-Path "frontend/.env")) {
        Write-ColorOutput "📝 Creating frontend/.env..." $Cyan
        @"
# API Configuration
VITE_API_BASE_URL=http://localhost:3000

# Supabase Configuration
VITE_SUPABASE_URL=your-supabase-url-here
VITE_SUPABASE_ANON_KEY=your-anon-key-here

# Development Settings
VITE_ENVIRONMENT=development
"@ | Out-File -FilePath "frontend/.env" -Encoding UTF8
        Write-ColorOutput "✅ Created frontend/.env (please update with your actual values)" $Green
    }

    # Root .env.example
    if (!(Test-Path ".env.example")) {
        Write-ColorOutput "📝 Creating .env.example..." $Cyan
        @"
# Copy this file to .env and fill in your actual values

# Supabase Configuration
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key

# JWT Configuration
JWT_SECRET_KEY=your-secure-random-key-here
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30

# Development Settings
DEBUG=True
ENVIRONMENT=development

# CORS Settings
ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000
"@ | Out-File -FilePath ".env.example" -Encoding UTF8
    }
}

function Validate-Setup {
    Write-ColorOutput "🔍 Validating setup..." $Cyan

    $issues = @()

    # Check required files exist
    $requiredFiles = @(
        "backend/requirements.txt",
        "frontend/package.json",
        "backend/main.py",
        "frontend/src/main.tsx",
        ".pre-commit-config.yaml"
    )

    foreach ($file in $requiredFiles) {
        if (!(Test-Path $file)) {
            $issues += "Missing required file: $file"
        }
    }

    # Check Python virtual environment
    if (!(Test-Path "backend/venv")) {
        $issues += "Python virtual environment not created"
    }

    # Check Node modules
    if (!(Test-Path "frontend/node_modules")) {
        $issues += "Node.js dependencies not installed"
    }

    if ($issues.Count -gt 0) {
        Write-ColorOutput "❌ Setup validation failed:" $Red
        foreach ($issue in $issues) {
            Write-ColorOutput "   - $issue" $Red
        }
        return $false
    }

    Write-ColorOutput "✅ Setup validation passed" $Green
    return $true
}

function Show-NextSteps {
    Write-ColorOutput "`n🎉 Development environment setup complete!" $Green
    Write-ColorOutput "=" * 50 $Cyan
    Write-ColorOutput "📋 Next steps:" $Yellow
    Write-ColorOutput "   1. Update .env files with your Supabase credentials" $White
    Write-ColorOutput "   2. Run '.\start-dev-enhanced.ps1' to start development" $White
    Write-ColorOutput "   3. Open http://localhost:5173 in your browser" $White
    Write-ColorOutput "   4. Check API docs at http://localhost:8000/docs" $White
    Write-ColorOutput "=" * 50 $Cyan
    Write-ColorOutput "💡 Available commands:" $Yellow
    Write-ColorOutput "   .\start-dev-enhanced.ps1    - Start development environment" $White
    Write-ColorOutput "   pre-commit run --all-files - Run all pre-commit checks" $White
    Write-ColorOutput "   pytest backend/tests/       - Run backend tests" $White
    Write-ColorOutput "   npm test                   - Run frontend tests" $White
    Write-ColorOutput "=" * 50 $Cyan
}

# Main execution
Write-ColorOutput "🚀 Setting up Reserve Flow AI 2026 Development Environment" $Green
Write-ColorOutput "=" * 60 $Cyan

# Install Python dependencies
if (!(Install-PythonDependencies)) {
    Write-ColorOutput "❌ Python setup failed" $Red
    exit 1
}

# Install Node.js dependencies
if (!(Install-NodeDependencies)) {
    Write-ColorOutput "❌ Node.js setup failed" $Red
    exit 1
}

# Setup pre-commit hooks
if (!$SkipPreCommit) {
    if (!(Setup-PreCommit)) {
        Write-ColorOutput "❌ Pre-commit setup failed" $Red
        exit 1
    }
}

# Create environment files
Create-EnvironmentFiles

# Validate setup
if (!(Validate-Setup)) {
    Write-ColorOutput "❌ Setup validation failed" $Red
    exit 1
}

# Show next steps
Show-NextSteps
