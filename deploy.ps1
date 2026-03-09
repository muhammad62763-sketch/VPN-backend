# VPN Backend - Vercel Deployment Script (PowerShell)
# Usage: .\deploy.ps1 [production|preview]

param(
    [string]$DeployType = "preview"
)

Write-Host "🚀 VPN Backend Deployment Script" -ForegroundColor Cyan
Write-Host "==================================" -ForegroundColor Cyan
Write-Host ""

# Check if vercel CLI is installed
$vercelInstalled = Get-Command vercel -ErrorAction SilentlyContinue
if (-not $vercelInstalled) {
    Write-Host "❌ Vercel CLI not found. Installing..." -ForegroundColor Red
    npm install -g vercel
}

# Determine deployment type
if ($DeployType -eq "production") {
    Write-Host "📦 Deploying to PRODUCTION..." -ForegroundColor Yellow
    $deployCmd = "vercel --prod"
} else {
    Write-Host "📦 Deploying to PREVIEW..." -ForegroundColor Green
    $deployCmd = "vercel"
}

# Pre-deployment checks
Write-Host ""
Write-Host "🔍 Running pre-deployment checks..." -ForegroundColor Cyan

# Check if .env exists
if (-not (Test-Path ".env")) {
    Write-Host "⚠️  Warning: .env file not found" -ForegroundColor Yellow
    Write-Host "   Make sure environment variables are set in Vercel Dashboard" -ForegroundColor Yellow
}

# Check if vercel.json exists
if (-not (Test-Path "vercel.json")) {
    Write-Host "❌ Error: vercel.json not found" -ForegroundColor Red
    exit 1
}

# Check if api/index.py exists
if (-not (Test-Path "api/index.py")) {
    Write-Host "❌ Error: api/index.py not found" -ForegroundColor Red
    exit 1
}

Write-Host "✅ Pre-deployment checks passed" -ForegroundColor Green

# Run security scan (optional)
Write-Host ""
Write-Host "🔒 Running security scan..." -ForegroundColor Cyan
$banditInstalled = Get-Command bandit -ErrorAction SilentlyContinue
if ($banditInstalled) {
    bandit -r app/ -ll
    if ($LASTEXITCODE -ne 0) {
        Write-Host "⚠️  Security warnings found (review before deploying)" -ForegroundColor Yellow
    }
} else {
    Write-Host "⚠️  Bandit not installed, skipping security scan" -ForegroundColor Yellow
}

# Deploy
Write-Host ""
Write-Host "🚀 Deploying to Vercel..." -ForegroundColor Cyan
Invoke-Expression $deployCmd

Write-Host ""
Write-Host "✅ Deployment complete!" -ForegroundColor Green
Write-Host ""
Write-Host "📝 Next steps:" -ForegroundColor Cyan
Write-Host "1. Test the deployment URL"
Write-Host "2. Check logs: vercel logs --follow"
Write-Host "3. Monitor for errors"
Write-Host "4. Update frontend API URL if needed"
