#!/bin/bash

# VPN Backend - Vercel Deployment Script
# Usage: ./deploy.sh [production|preview]

set -e

echo "🚀 VPN Backend Deployment Script"
echo "=================================="

# Check if vercel CLI is installed
if ! command -v vercel &> /dev/null; then
    echo "❌ Vercel CLI not found. Installing..."
    npm install -g vercel
fi

# Determine deployment type
DEPLOY_TYPE=${1:-preview}

if [ "$DEPLOY_TYPE" = "production" ]; then
    echo "📦 Deploying to PRODUCTION..."
    DEPLOY_CMD="vercel --prod"
else
    echo "📦 Deploying to PREVIEW..."
    DEPLOY_CMD="vercel"
fi

# Pre-deployment checks
echo ""
echo "🔍 Running pre-deployment checks..."

# Check if .env exists (for reference, not deployed)
if [ ! -f ".env" ]; then
    echo "⚠️  Warning: .env file not found"
    echo "   Make sure environment variables are set in Vercel Dashboard"
fi

# Check if vercel.json exists
if [ ! -f "vercel.json" ]; then
    echo "❌ Error: vercel.json not found"
    exit 1
fi

# Check if api/index.py exists
if [ ! -f "api/index.py" ]; then
    echo "❌ Error: api/index.py not found"
    exit 1
fi

echo "✅ Pre-deployment checks passed"

# Run security scan (optional)
echo ""
echo "🔒 Running security scan..."
if command -v bandit &> /dev/null; then
    bandit -r app/ -ll || echo "⚠️  Security warnings found (review before deploying)"
else
    echo "⚠️  Bandit not installed, skipping security scan"
fi

# Deploy
echo ""
echo "🚀 Deploying to Vercel..."
$DEPLOY_CMD

echo ""
echo "✅ Deployment complete!"
echo ""
echo "📝 Next steps:"
echo "1. Test the deployment URL"
echo "2. Check logs: vercel logs --follow"
echo "3. Monitor for errors"
echo "4. Update frontend API URL if needed"
