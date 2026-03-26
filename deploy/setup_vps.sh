#!/bin/bash
# =============================================
# LogiSteril ISTUL — Script de despliegue VPS
# Ubuntu 20.04 / 22.04 / Debian 11
# Ejecutar como: sudo bash deploy/setup_vps.sh
# =============================================

set -e  # Detener si hay error

APP_DIR="/var/www/logisteril"
REPO_URL="https://github.com/TU_USUARIO/logisteril-istul.git"  # <- CAMBIAR
SERVICE_NAME="logisteril"

echo "============================================"
echo " LogiSteril ISTUL — Setup VPS"
echo "============================================"

# 1. Actualizar sistema
echo "[1/9] Actualizando sistema..."
apt-get update -q
apt-get install -y -q python3 python3-pip python3-venv nginx git

# 2. Crear directorio de la app
echo "[2/9] Creando directorio /var/www/logisteril..."
mkdir -p $APP_DIR
mkdir -p /var/log/logisteril

# 3. Clonar repositorio
echo "[3/9] Clonando repositorio..."
if [ -d "$APP_DIR/.git" ]; then
    cd $APP_DIR && git pull
    echo "  → Repositorio actualizado"
else
    git clone $REPO_URL $APP_DIR
    echo "  → Repositorio clonado"
fi
cd $APP_DIR

# 4. Crear entorno virtual
echo "[4/9] Creando entorno virtual Python..."
python3 -m venv venv
source venv/bin/activate

# 5. Instalar dependencias
echo "[5/9] Instalando dependencias Python..."
pip install -r requirements.txt -q

# 6. Configurar variables de entorno
if [ ! -f "$APP_DIR/.env" ]; then
    echo "[6/9] Creando archivo .env..."
    cp .env.example .env
    SECRET=$(python3 -c "import secrets; print(secrets.token_hex(32))")
    sed -i "s/cambia-esta-clave-por-una-muy-segura-y-larga-2024/$SECRET/" .env
    sed -i "s/FLASK_ENV=development/FLASK_ENV=production/" .env
    sed -i "s/FLASK_DEBUG=1/FLASK_DEBUG=0/" .env
    echo "  → .env creado con SECRET_KEY aleatoria"
    echo "  ⚠️  Edita $APP_DIR/.env para configurar DATABASE_URL si usas PostgreSQL"
else
    echo "[6/9] .env ya existe, omitiendo..."
fi

# 7. Permisos
echo "[7/9] Configurando permisos..."
chown -R www-data:www-data $APP_DIR
chown -R www-data:www-data /var/log/logisteril
chmod -R 755 $APP_DIR

# 8. Instalar servicio systemd
echo "[8/9] Instalando servicio systemd..."
cp deploy/logisteril.service /etc/systemd/system/logisteril.service
systemctl daemon-reload
systemctl enable $SERVICE_NAME
systemctl restart $SERVICE_NAME
echo "  → Servicio $SERVICE_NAME activo"

# 9. Configurar Nginx
echo "[9/9] Configurando Nginx..."
cp deploy/nginx.conf /etc/nginx/sites-available/logisteril
ln -sf /etc/nginx/sites-available/logisteril /etc/nginx/sites-enabled/logisteril
# Desactivar default si existe
rm -f /etc/nginx/sites-enabled/default
nginx -t && systemctl reload nginx
echo "  → Nginx configurado"

echo ""
echo "============================================"
echo " ✅ Despliegue completado"
echo "============================================"
echo ""
echo " App corriendo en:  http://$(curl -s ifconfig.me)"
echo " Servicio:          systemctl status $SERVICE_NAME"
echo " Logs app:          tail -f /var/log/logisteril/error.log"
echo " Logs nginx:        tail -f /var/log/nginx/logisteril_error.log"
echo ""
echo " ⚠️  Para SSL con HTTPS (recomendado):"
echo "    apt install certbot python3-certbot-nginx"
echo "    certbot --nginx -d tudominio.com"
echo ""
