# 🧹 Script de nettoyage pour eTickets
# Supprime tous les fichiers temporaires et de cache

# Nettoyage Python
Remove-Item -Recurse -Force -ErrorAction SilentlyContinue @(
    Get-ChildItem -Path . -Recurse -Name "__pycache__" -Directory | 
    Where-Object { $_ -notlike "*\.venv\*" }
)

# Suppression des fichiers de cache Python
Get-ChildItem -Path . -Recurse -Include "*.pyc", "*.pyo" | 
Where-Object { $_.FullName -notlike "*\.venv\*" } | 
Remove-Item -Force -ErrorAction SilentlyContinue

# Nettoyage Django
Remove-Item -Force -ErrorAction SilentlyContinue @(
    ".\db.sqlite3",
    ".\staticfiles\*"
)

# Nettoyage des médias (QR codes générés)
Remove-Item -Recurse -Force -ErrorAction SilentlyContinue ".\media\*"

# Garder le .gitkeep dans media
if (-not (Test-Path ".\media\.gitkeep")) {
    New-Item -ItemType File -Path ".\media\.gitkeep" -Force
    Add-Content -Path ".\media\.gitkeep" -Value "# Dossier media pour les QR codes des tickets"
}

# Nettoyage des tests
Remove-Item -Recurse -Force -ErrorAction SilentlyContinue @(
    ".\.coverage",
    ".\htmlcov",
    ".\.pytest_cache"
)

# Nettoyage logs
Get-ChildItem -Path . -Recurse -Include "*.log" | 
Remove-Item -Force -ErrorAction SilentlyContinue

Write-Host "✅ Nettoyage terminé !" -ForegroundColor Green
Write-Host "📁 Fichiers supprimés :" -ForegroundColor Yellow
Write-Host "   - Dossiers __pycache__" -ForegroundColor Gray
Write-Host "   - Fichiers *.pyc, *.pyo" -ForegroundColor Gray  
Write-Host "   - Base de données SQLite" -ForegroundColor Gray
Write-Host "   - Fichiers média générés" -ForegroundColor Gray
Write-Host "   - Rapports de couverture" -ForegroundColor Gray
Write-Host "   - Fichiers de log" -ForegroundColor Gray
Write-Host ""
Write-Host "🔄 Pour recréer l'environnement :" -ForegroundColor Cyan
Write-Host "   python manage.py migrate" -ForegroundColor White
Write-Host "   python manage.py seed_offers" -ForegroundColor White
Write-Host "   python scripts/create_superuser.py --default" -ForegroundColor White