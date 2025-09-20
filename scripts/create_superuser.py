#!/usr/bin/env python
"""
Script de création automatique de super utilisateur pour eTickets
Usage: python scripts/create_superuser.py
"""

import os
import sys
import django
from pathlib import Path

# Configuration Django
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'etickets.settings')

try:
    django.setup()
except Exception as e:
    print(f"❌ Erreur de configuration Django: {e}")
    sys.exit(1)

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
import getpass


def create_superuser():
    """Créer un super utilisateur de manière interactive ou automatique"""
    
    print("🏆 === Création du Super Utilisateur eTickets ===")
    print()
    
    # Vérifier s'il y a déjà un super utilisateur
    existing_superusers = User.objects.filter(is_superuser=True)
    if existing_superusers.exists():
        print("👑 Super utilisateurs existants:")
        for user in existing_superusers:
            print(f"   - {user.username} ({user.email})")
        print()
        
        response = input("🤔 Voulez-vous créer un autre super utilisateur ? (y/N): ")
        if response.lower() not in ['y', 'yes', 'oui', 'o']:
            print("✅ Opération annulée")
            return
    
    # Collecte des informations
    print("📝 Saisissez les informations du super utilisateur:")
    print()
    
    # Nom d'utilisateur
    while True:
        username = input("👤 Nom d'utilisateur: ").strip()
        if not username:
            print("❌ Le nom d'utilisateur ne peut pas être vide")
            continue
            
        if User.objects.filter(username=username).exists():
            print(f"❌ L'utilisateur '{username}' existe déjà")
            continue
            
        # Validation basique du nom d'utilisateur
        if not username.replace('_', '').replace('-', '').replace('.', '').replace('@', '').replace('+', '').isalnum():
            print("❌ Nom d'utilisateur invalide. Utilisez seulement: lettres, chiffres, @, ., +, -, _")
            continue
            
        break
    
    # Email
    while True:
        email = input("📧 Email (optionnel): ").strip()
        if not email:
            email = f"{username}@etickets.local"
            print(f"📧 Email par défaut: {email}")
            break
            
        # Validation basique de l'email
        if '@' not in email or '.' not in email.split('@')[1]:
            print("❌ Format d'email invalide")
            continue
            
        break
    
    # Mot de passe
    while True:
        password1 = getpass.getpass("🔒 Mot de passe: ")
        if not password1:
            print("❌ Le mot de passe ne peut pas être vide")
            continue
            
        password2 = getpass.getpass("🔒 Confirmez le mot de passe: ")
        
        if password1 != password2:
            print("❌ Les mots de passe ne correspondent pas")
            continue
            
        # Validation basique
        if len(password1) < 8:
            response = input("⚠️  Mot de passe court (<8 caractères). Continuer ? (y/N): ")
            if response.lower() not in ['y', 'yes', 'oui', 'o']:
                continue
        
        break
    
    # Confirmation finale
    print()
    print("📋 Récapitulatif:")
    print(f"   👤 Nom d'utilisateur: {username}")
    print(f"   📧 Email: {email}")
    print(f"   👑 Permissions: Super Utilisateur")
    print()
    
    response = input("✅ Créer ce super utilisateur ? (Y/n): ")
    if response.lower() in ['n', 'no', 'non']:
        print("❌ Création annulée")
        return
    
    # Création de l'utilisateur
    try:
        user = User.objects.create_superuser(
            username=username,
            email=email,
            password=password1
        )
        
        print()
        print("🎉 Super utilisateur créé avec succès !")
        print(f"👤 Nom d'utilisateur: {user.username}")
        print(f"📧 Email: {user.email}")
        print(f"🆔 ID: {user.id}")
        print()
        print("🔗 Vous pouvez maintenant vous connecter à l'administration:")
        print("   http://127.0.0.1:8000/admin/")
        print()
        
    except ValidationError as e:
        print(f"❌ Erreur de validation: {e}")
    except Exception as e:
        print(f"❌ Erreur lors de la création: {e}")


def create_default_superuser():
    """Créer un super utilisateur par défaut (pour développement)"""
    
    print("🚀 Création d'un super utilisateur par défaut...")
    
    # Paramètres par défaut
    username = "admin"
    email = "admin@etickets.local"
    password = "AdminPass123!"
    
    # Vérifier si l'utilisateur existe déjà
    if User.objects.filter(username=username).exists():
        print(f"⚠️  L'utilisateur '{username}' existe déjà")
        user = User.objects.get(username=username)
        user.is_staff = True
        user.is_superuser = True
        user.set_password(password)
        user.save()
        print("✅ Permissions mises à jour")
    else:
        user = User.objects.create_superuser(
            username=username,
            email=email,
            password=password
        )
        print("✅ Super utilisateur créé")
    
    print()
    print("📝 Informations de connexion:")
    print(f"   👤 Username: {username}")
    print(f"   🔒 Password: {password}")
    print(f"   🔗 URL: http://127.0.0.1:8000/admin/")
    print()


if __name__ == "__main__":
    # Vérifier les arguments de ligne de commande
    if len(sys.argv) > 1 and sys.argv[1] == "--default":
        create_default_superuser()
    else:
        create_superuser()