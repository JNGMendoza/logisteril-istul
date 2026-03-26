#!/bin/bash
# =============================================
# LogiSteril ISTUL — Actualizar versión en VPS
# Ejecutar como: sudo bash deploy/actualizar.sh
# =============================================

APP_DIR="/var/www/logisteril"
SERVICE_NAME="logisteril"

echo "🔄 Actualizando LogiSteril..."

cd $APP_DIR

# Pull últimos cambios de GitHub
git pull origin main

# Activar entorno virtual y actualizar dependencias
source venv/bin/activate
pip install -r requirements.txt -q

# Reiniciar servicio
systemctl restart $SERVICE_NAME

echo "✅ Actualización completada"
echo "   Estado: $(systemctl is-active $SERVICE_NAME)"
