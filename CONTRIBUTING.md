# Contribuer au projet eticketsv10

Merci de vouloir contribuer ! Ce document décrit rapidement comment préparer l'environnement, soumettre des issues et ouvrir des pull requests.

## Règles générales
- Fork → branche feature/bugfix → PR vers `main`.
- Écrire des commits clairs et atomiques.
- Ajouter/mettre à jour les tests pour tout nouveau comportement.
- Respecter le style de code (Black + Ruff).

## Installation locale (exemple)
1. Cloner le dépôt :
   git clone https://github.com/sheerif/eticketsv10.git
2. Créer un environnement virtuel :
   python -m venv .venv && source .venv/bin/activate
3. Installer les dépendances :
   pip install -r requirements.txt
4. Configurer les variables d'environnement :
   cp .env.example .env
   puis éditer `.env` avec les paramètres locaux.

## Tests
- Lancer la suite de tests :
  pytest
- Nous utilisons `pytest` et la configuration se trouve dans `pytest.ini`.

## Pré-commit
- Installe et active pre-commit :
  pip install pre-commit
  pre-commit install
- Exécute les hooks localement :
  pre-commit run --all-files

## Pull Requests
- Remplissez le template de PR.
- Assurez-vous que CI passe (tests + linters).
- Décrivez le but de la PR, les changements et les étapes pour tester.

## Communication
- Ouvrez une issue si vous proposez une grosse modification avant de coder.