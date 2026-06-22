# Script para iniciar o backend MCJB Chatbot
Write-Host "=== Iniciando Backend MCJB Chatbot ===" -ForegroundColor Green

# Verificar se o ambiente virtual existe
if (-not (Test-Path ".\venv")) {
    Write-Host "Criando ambiente virtual Python..." -ForegroundColor Yellow
    python -m venv venv
}

# Ativar ambiente virtual
Write-Host "Ativando ambiente virtual..." -ForegroundColor Yellow
.\venv\Scripts\Activate.ps1

# Instalar dependencias
Write-Host "Instalando dependencias..." -ForegroundColor Yellow
pip install -r backend\requirements.txt --quiet

# Iniciar servidor
Write-Host "Iniciando servidor FastAPI na porta 8000..." -ForegroundColor Green
uvicorn backend.main:app --reload --port 8000
python -m venv venv