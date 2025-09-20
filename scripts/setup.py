#!/usr/bin/env python
"""
Script de configuration initiale pour eTickets
Initialise la base de données, créé les données de base et le super utilisateur
Usage: python scripts/setup.py
"""

import os
import sys
import subprocess
import django
from pathlib import Path

# Configuration Django
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'etickets.settings')

def run_command(command, description):
    """Exécuter une commande avec affichage du statut"""
    print(f"🔧 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, 
                              capture_output=True, text=True, cwd=BASE_DIR)
        print(f"✅ {description} - OK")
        if result.stdout.strip():
            print(f"   {result.stdout.strip()}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} - ERREUR")
        if e.stderr:
            print(f"   Erreur: {e.stderr.strip()}")
        return False

def setup_project():
    """Configuration complète du projet"""
    
    print("🏆 === Configuration initiale eTickets ===")
    print()
    
    # Vérifier que nous sommes dans le bon dossier
    if not (BASE_DIR / 'manage.py').exists():
        print("❌ Erreur: manage.py introuvable")
        print("   Assurez-vous d'être dans le dossier racine du projet")
        return False
    
    # Étapes de configuration
    steps = [
        ("python manage.py makemigrations", "Génération des migrations"),
        ("python manage.py migrate", "Application des migrations"),
        ("python manage.py collectstatic --noinput", "Collecte des fichiers statiques"),
        ("python manage.py seed_offers", "Création des offres de base"),
    ]
    
    # Exécution des étapes
    success_count = 0
    for command, description in steps:
        if run_command(command, description):
            success_count += 1
    
    print()
    
    # Création du super utilisateur
    if success_count == len(steps):
        print("👑 Création du super utilisateur...")
        try:
            django.setup()
            from django.contrib.auth.models import User
            
            # Super utilisateur par défaut
            username = "admin"
            email = "admin@etickets.local"
            password = "AdminPass123!"
            
            user, created = User.objects.get_or_create(
                username=username,
                defaults={"email": email}
            )
            user.is_staff = True
            user.is_superuser = True
            user.set_password(password)
            user.save()
            
            print(f"✅ Super utilisateur {'créé' if created else 'mis à jour'}")
            print()
            
        except Exception as e:
            print(f"❌ Erreur lors de la création du super utilisateur: {e}")
            return False
    
    # Résumé final
    if success_count == len(steps):
        print("🎉 Configuration terminée avec succès !")
        print()
        print("📝 Informations de connexion admin:")
        print(f"   👤 Username: admin")
        print(f"   🔒 Password: AdminPass123!")
        print(f"   🔗 URL: http://127.0.0.1:8000/admin/")
        print()
        print("🚀 Pour démarrer le serveur:")
        print("   python manage.py runserver")
        print()
        return True
    else:
        print(f"⚠️  Configuration incomplète ({success_count}/{len(steps)} étapes réussies)")
        return False

if __name__ == "__main__":
    success = setup_project()
    sys.exit(0 if success else 1)