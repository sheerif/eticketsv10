#!/usr/bin/env python
"""
Script de vérification de l'état du projet eTickets
Vérifie que tous les composants sont correctement configurés
Usage: python scripts/check_project.py
"""

import os
import sys
import subprocess
from pathlib import Path

def check_file_exists(file_path, description):
    """Vérifier qu'un fichier existe"""
    if Path(file_path).exists():
        print(f"✅ {description}")
        return True
    else:
        print(f"❌ {description} - MANQUANT")
        return False

def check_directory_clean(directory, description):
    """Vérifier qu'un dossier est propre (pas de cache)"""
    cache_files = list(Path(directory).rglob("__pycache__"))
    # Exclure .venv du check
    cache_files = [f for f in cache_files if '.venv' not in str(f)]
    
    if not cache_files:
        print(f"✅ {description} - Propre")
        return True
    else:
        print(f"⚠️  {description} - {len(cache_files)} dossiers cache trouvés")
        return False

def check_git_status():
    """Vérifier l'état Git"""
    try:
        result = subprocess.run(['git', 'status', '--porcelain'], 
                              capture_output=True, text=True, check=True)
        
        if not result.stdout.strip():
            print("✅ Git - Aucune modification non commitée")
            return True
        else:
            print("⚠️  Git - Modifications non commitées détectées")
            return False
    except subprocess.CalledProcessError:
        print("❌ Git - Erreur lors de la vérification")
        return False

def check_python_files():
    """Vérifier qu'il n'y a pas de fichiers .pyc"""
    pyc_files = list(Path('.').rglob("*.pyc"))
    pyc_files = [f for f in pyc_files if '.venv' not in str(f)]
    
    if not pyc_files:
        print("✅ Fichiers Python - Aucun .pyc trouvé")
        return True
    else:
        print(f"⚠️  Fichiers Python - {len(pyc_files)} fichiers .pyc trouvés")
        return False

def check_media_directory():
    """Vérifier le dossier media"""
    media_files = list(Path('media').glob('*'))
    media_files = [f for f in media_files if f.name != '.gitkeep']
    
    if not media_files:
        print("✅ Dossier media - Propre (uniquement .gitkeep)")
        return True
    else:
        print(f"⚠️  Dossier media - {len(media_files)} fichiers trouvés")
        return False

def main():
    """Vérification complète du projet"""
    print("🔍 === Vérification du projet eTickets ===")
    print()
    
    checks = []
    
    # Fichiers essentiels
    print("📄 Fichiers essentiels:")
    checks.append(check_file_exists(".gitignore", ".gitignore présent"))
    checks.append(check_file_exists(".env.example", ".env.example présent"))
    checks.append(check_file_exists(".env.docker.example", ".env.docker.example présent"))
    checks.append(check_file_exists("requirements.txt", "requirements.txt présent"))
    checks.append(check_file_exists("manage.py", "manage.py présent"))
    print()
    
    # Scripts d'automatisation
    print("🔧 Scripts d'automatisation:")
    checks.append(check_file_exists("scripts/setup.py", "Script de configuration"))
    checks.append(check_file_exists("scripts/create_superuser.py", "Script super utilisateur"))
    checks.append(check_file_exists("scripts/cleanup.ps1", "Script de nettoyage"))
    print()
    
    # Tests
    print("🧪 Suite de tests:")
    checks.append(check_file_exists("tests/test_e2e_integration.py", "Tests E2E"))
    checks.append(check_file_exists("tests/test_edge_cases.py", "Tests edge cases"))
    checks.append(check_file_exists("core/tests/test_security.py", "Tests sécurité"))
    checks.append(check_file_exists("accounts/tests/test_views_extended.py", "Tests vues accounts"))
    checks.append(check_file_exists("orders/tests/test_views_extended.py", "Tests vues orders"))
    checks.append(check_file_exists("tickets/tests/test_api_extended.py", "Tests API tickets"))
    print()
    
    # Docker
    print("🐳 Configuration Docker:")
    checks.append(check_file_exists("Dockerfile", "Dockerfile présent"))
    checks.append(check_file_exists("docker-compose.yml", "docker-compose.yml présent"))
    checks.append(check_file_exists("docker/entrypoint.sh", "Script entrypoint"))
    print()
    
    # Propreté du projet
    print("🧹 Propreté du projet:")
    checks.append(check_directory_clean(".", "Dossiers cache Python"))
    checks.append(check_python_files())
    checks.append(check_media_directory())
    checks.append(check_git_status())
    print()
    
    # Base de données
    print("🗄️  Base de données:")
    if Path("db.sqlite3").exists():
        print("⚠️  db.sqlite3 - Base de données présente (OK pour dev)")
        checks.append(True)
    else:
        print("✅ db.sqlite3 - Pas de base présente (propre pour Git)")
        checks.append(True)
    print()
    
    # Résumé
    passed = sum(checks)
    total = len(checks)
    percentage = (passed / total) * 100
    
    print("=" * 50)
    if percentage == 100:
        print(f"🎉 PARFAIT ! {passed}/{total} vérifications réussies")
        print("✅ Le projet est prêt pour Git et déploiement")
    elif percentage >= 90:
        print(f"🟢 TRÈS BIEN ! {passed}/{total} vérifications réussies ({percentage:.0f}%)")
        print("✅ Le projet est en bon état")
    elif percentage >= 70:
        print(f"🟡 BIEN ! {passed}/{total} vérifications réussies ({percentage:.0f}%)")
        print("⚠️  Quelques améliorations suggérées")
    else:
        print(f"🔴 À AMÉLIORER ! {passed}/{total} vérifications réussies ({percentage:.0f}%)")
        print("❌ Plusieurs éléments nécessitent attention")
    
    print()
    print("🚀 Pour commencer le développement:")
    print("   python scripts/setup.py")
    print("   python manage.py runserver")
    
    return percentage == 100

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)