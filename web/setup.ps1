Write-Host "=== CAI DAT DO AN TUYEN DUNG ===" -ForegroundColor Cyan
if (-not (Test-Path ".venv")) { python -m venv .venv }
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
if (-not (Test-Path ".env")) { Copy-Item .env.example .env }
Write-Host "Hoan tat. Chay: python scripts\test_connections.py" -ForegroundColor Green
Write-Host "Sau do: python app.py" -ForegroundColor Green
