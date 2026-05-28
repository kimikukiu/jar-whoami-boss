# Creează repository GitHub automat
param(
    [Parameter(Mandatory=$true)]
    [string]$Token,
    
    [string]$RepoName = "jar-whoami-boss",
    [string]$Description = "JARVIS Supreme Commander - AI Agent Ecosystem",
    [switch]$Private
)

$headers = @{
    "Authorization" = "token $Token"
    "Accept" = "application/vnd.github.v3+json"
}

$body = @{
    name = $RepoName
    description = $Description
    private = $Private.IsPresent
    auto_init = $false
} | ConvertTo-Json

try {
    Write-Host "Creare repository GitHub: $RepoName..." -ForegroundColor Cyan
    $response = Invoke-RestMethod -Uri "https://api.github.com/user/repos" -Method Post -Headers $headers -Body $body
    
    Write-Host "✅ Repository creat cu succes!" -ForegroundColor Green
    Write-Host "   URL: $($response.html_url)" -ForegroundColor Cyan
    
    # Push codul local
    Write-Host "`nPush cod local..." -ForegroundColor Yellow
    git remote remove origin 2>$null
    git remote add origin "https://$Token@github.com/$(($response.owner.login))/$RepoName.git"
    git branch -M main
    git push -u origin main --force
    
    Write-Host "`n✅ GATA! Repository disponibil la:" -ForegroundColor Green
    Write-Host "   $($response.html_url)" -ForegroundColor Cyan
    
} catch {
    Write-Host "`n❌ EROARE: $($_.Exception.Message)" -ForegroundColor Red
    
    if ($_.Exception.Response) {
        $reader = New-Object System.IO.StreamReader($_.Exception.Response.GetResponseStream())
        $reader.BaseStream.Position = 0
        $reader.DiscardBufferedData()
        $errorBody = $reader.ReadToEnd()
        Write-Host "Detalii: $errorBody" -ForegroundColor Yellow
    }
}

Write-Host "`nApasă orice tastă pentru a ieși..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
