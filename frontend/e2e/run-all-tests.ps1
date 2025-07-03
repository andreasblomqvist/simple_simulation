# PowerShell script to run all Playwright E2E tests
# This script ensures both backend and frontend are running before executing tests

Write-Host "🚀 Starting Comprehensive Scenario CRUD E2E Testing..." -ForegroundColor Green

# Check if backend is running
Write-Host "📡 Checking backend server..." -ForegroundColor Yellow
$backendResponse = $null
try {
    $backendResponse = Invoke-RestMethod -Uri "http://localhost:8000/health" -Method GET -TimeoutSec 5
    Write-Host "✅ Backend is running" -ForegroundColor Green
} catch {
    Write-Host "❌ Backend is not running. Please start the backend server first." -ForegroundColor Red
    Write-Host "   Run: `$env:PYTHONPATH='.'; python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000" -ForegroundColor Yellow
    exit 1
}

# Check if frontend is running
Write-Host "🌐 Checking frontend server..." -ForegroundColor Yellow
$frontendResponse = $null
try {
    $frontendResponse = Invoke-WebRequest -Uri "http://localhost:3000" -Method GET -TimeoutSec 5
    Write-Host "✅ Frontend is running" -ForegroundColor Green
} catch {
    Write-Host "❌ Frontend is not running. Please start the frontend server first." -ForegroundColor Red
    Write-Host "   Run: cd frontend; npm run dev" -ForegroundColor Yellow
    exit 1
}

# Run the tests
Write-Host "🧪 Running Playwright E2E tests..." -ForegroundColor Green
Write-Host "   This will test:" -ForegroundColor Cyan
Write-Host "   - Scenario CRUD operations (Create, Read, Update, Delete)" -ForegroundColor Cyan
Write-Host "   - Scenario comparison functionality" -ForegroundColor Cyan
Write-Host "   - Error handling and edge cases" -ForegroundColor Cyan
Write-Host "   - Form validation" -ForegroundColor Cyan
Write-Host "   - Export functionality" -ForegroundColor Cyan
Write-Host ""

# Run tests with headed browser for visibility
Write-Host "🎭 Running tests with headed browser..." -ForegroundColor Yellow
npm run test:e2e:headed

# Check if tests passed
if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "🎉 All E2E tests passed successfully!" -ForegroundColor Green
    Write-Host "📊 To view detailed test report, run: npm run test:e2e:report" -ForegroundColor Cyan
} else {
    Write-Host ""
    Write-Host "❌ Some E2E tests failed. Check the output above for details." -ForegroundColor Red
    Write-Host "🔍 To debug tests, run: npm run test:e2e:debug" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "📋 Test Summary:" -ForegroundColor Green
Write-Host "   - Scenario CRUD: Create, Read, Update, Delete operations" -ForegroundColor White
Write-Host "   - Scenario Comparison: Side-by-side comparison functionality" -ForegroundColor White
Write-Host "   - Error Handling: Network errors, validation, edge cases" -ForegroundColor White
Write-Host "   - Performance: Large datasets, concurrent operations" -ForegroundColor White
Write-Host "   - Export: Excel export functionality" -ForegroundColor White 