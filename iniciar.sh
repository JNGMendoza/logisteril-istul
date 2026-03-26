#!/bin/bash
echo "============================================"
echo " LogiSteril ISTUL - Iniciando sistema..."
echo "============================================"

if [ ! -d "venv" ]; then
    echo "Creando entorno virtual..."
    python3 -m venv venv
fi

source venv/bin/activate

echo "Instalando dependencias..."
pip install -r requirements.txt -q

echo ""
echo "Iniciando servidor..."
echo "Abre tu navegador en: http://localhost:5000"
echo "Presiona Ctrl+C para detener."
echo ""

python app.py
