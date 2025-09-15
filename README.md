<<<<<<< HEAD
# e-Tickets JO — Clean Start V8

Front dynamique, panier, compte, paiement mock, QR, vérification et liste "Mes billets".

## Lancer (Windows PowerShell)
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_offers
python manage.py runserver
```
- Front: http://127.0.0.1:8000/offers/ (redir depuis /)
- Login: /login/ — Signup: /signup/
- Scan: /scan/
- Mes billets: /my/tickets/

## Tests
```powershell
python manage.py test
```
=======
# etickets-v10
EXAMEN BLOC 3 STUDI
>>>>>>> 3c9edfb2ffc61519caa5c935350a5ebbdb7da0fc
