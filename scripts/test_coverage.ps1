# Usage: right-click -> Run with PowerShell, or: pwsh -File scripts/test_coverage.ps1
pip install coverage
python manage.py test
coverage run manage.py test
coverage report -m
coverage html
Start-Process .\htmlcov\index.html
