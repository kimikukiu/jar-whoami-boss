# Script automat pentru creare repo GitHub și push
$Token = "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"
$RepoName = "jar-whoami-boss"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host " CREARE AUTOMATA REPO GITHUB" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# Creare repository via GitHub API
$headers = @{
    "Authorization" = "token $Token"
    "Accept" = "application/vnd.github.v3+json"
}

$body = @{
    name = $RepoName
    description = "JARVIS Supreme Commander - AI Agent Ecosystem"
    private = $false
    auto_init = $false
} | ConvertTo-Json

try {
    Write-Host "`nCreare repository..." -ForegroundColor Yellow
    $response = Invoke-RestMethod -Uri "https://api.github.com/user/repos" -Method Post -Headers $headers -Body $body
    Write-Host "✅ Repository creat: $($response.html_url)" -ForegroundColor Green
    
    # Extrage username
    $username = $response.owner.login
    
    # Push cod local
    Write-Host "`nPush cod local..." -ForegroundColor Yellow
    Set-Location D:\jarvis\ecosystem
    
    git remote remove origin 2>$null
    git remote add origin "https://$Token@github.com/$username/$RepoName.git"
    
    git add README.md *.py *.bat *.ps1 *.txt .gitignore 2>$null
    git commit -m "Initial JARVIS commit" 2>$null
    
    git branch -M main
    git push -u origin main --force
    
    Write-Host "`n========================================" -ForegroundColor Green
    Write-Host " ✅ SUCCES! Repository disponibil:" -ForegroundColor Green
    Write-Host " https://github.com/$username/$RepoName" -ForegroundColor Cyan
    Write-Host "========================================" -ForegroundColor Green
    
} catch {
    Write-Host "`n========================================" -ForegroundColor Red
    Write-Host " ❌ EROARE: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "========================================" -ForegroundColor Red
}

pause
