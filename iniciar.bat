@echo off
echo ============================================
echo  LogiSteril ISTUL - Iniciando sistema...
echo ============================================

if not exist venv (
    echo Creando entorno virtual...
    python -m venv venv
)

call venv\Scripts\activate

echo Instalando dependencias...
pip install -r requirements.txt -q

echo.
echo Iniciando servidor...
echo Abre tu navegador en: http://localhost:5000
echo Presiona Ctrl+C para detener.
echo.

python app.py
pause
