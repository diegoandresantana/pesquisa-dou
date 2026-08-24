#!/bin/bash
# Script para rodar o servidor do Portal DOU

echo "================================================"
echo "🚀 Iniciando Portal de Atos DOU"
echo "================================================"

# Verificar se requirements estão instalados
if ! python -c "import fastapi" 2>/dev/null; then
    echo "📦 Instalando dependências..."
    pip install -r requirements.txt
fi

# Iniciar o servidor
echo "🌐 Servidor iniciando em http://127.0.0.1:8000"
python server.py