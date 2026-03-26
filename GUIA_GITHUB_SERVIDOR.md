# Guía completa: GitHub + Servidor VPS
## LogiSteril ISTUL

---

## PARTE 1 — Subir a GitHub

### Paso 1: Crear repositorio en GitHub

1. Ir a [github.com](https://github.com) e iniciar sesión
2. Clic en **"New repository"** (botón verde)
3. Configurar:
   - **Repository name:** `logisteril-istul`
   - **Description:** `Plataforma de logística para Central de Esterilización ISTUL`
   - **Visibility:** Private ✅ *(recomendado para datos hospitalarios)*
   - **NO marcar** "Add a README file" (ya tenemos uno)
4. Clic **"Create repository"**

---

### Paso 2: Preparar Git en tu computadora

```bash
# Verificar que Git está instalado
git --version

# Si no está instalado (Windows): descargar de https://git-scm.com
# Si no está instalado (Ubuntu/Debian):
sudo apt install git
```

---

### Paso 3: Inicializar y subir el proyecto

Abrir terminal en la carpeta del proyecto `logisteril/`:

```bash
# Inicializar repositorio Git
git init

# Configurar tu identidad (solo la primera vez)
git config --global user.name "Tu Nombre"
git config --global user.email "tu@correo.com"

# Agregar todos los archivos
git add .

# Primer commit
git commit -m "feat: plataforma inicial LogiSteril ISTUL

- Login con roles (admin, supervisor, técnico)
- Módulo de inventario con alertas de stock
- Control de equipos y mantenimientos
- Trazabilidad de ciclos de esterilización
- Reportes imprimibles
- Gestión de usuarios"

# Conectar con GitHub (reemplaza TU_USUARIO con tu usuario de GitHub)
git remote add origin https://github.com/TU_USUARIO/logisteril-istul.git

# Subir a GitHub
git branch -M main
git push -u origin main
```

✅ ¡El código ya está en GitHub!

---

### Paso 4: Para subir cambios futuros

Cada vez que modifiques algo:

```bash
git add .
git commit -m "descripción breve del cambio"
git push
```

---

## PARTE 2 — Desplegar en servidor VPS

### Opción A: VPS propio (Ubuntu/Debian)

Necesitas: Un servidor con Ubuntu 20.04/22.04 con acceso SSH.
Servicios económicos: DigitalOcean ($6/mes), Hetzner (€4/mes), Linode, Vultr.

#### Conectarse al servidor

```bash
ssh root@IP_DE_TU_SERVIDOR
```

#### Clonar y desplegar con un solo comando

```bash
# Clonar el repositorio
git clone https://github.com/TU_USUARIO/logisteril-istul.git /var/www/logisteril

# Editar el script con tu URL de repositorio
nano /var/www/logisteril/deploy/setup_vps.sh
# Cambiar la línea: REPO_URL="https://github.com/TU_USUARIO/logisteril-istul.git"

# Ejecutar el script de instalación automática
sudo bash /var/www/logisteril/deploy/setup_vps.sh
```

El script instala automáticamente:
- Python 3, pip, virtualenv
- Nginx (servidor web)
- Gunicorn (servidor WSGI)
- Configura el servicio systemd para arranque automático

#### Comandos útiles en el servidor

```bash
# Ver estado del servicio
systemctl status logisteril

# Reiniciar la app
systemctl restart logisteril

# Ver logs en tiempo real
tail -f /var/log/logisteril/error.log

# Actualizar a nueva versión desde GitHub
sudo bash /var/www/logisteril/deploy/actualizar.sh
```

#### Configurar dominio (si tienes uno)

```bash
# Editar la configuración de Nginx
nano /etc/nginx/sites-available/logisteril
# Cambiar: server_name tudominio.com www.tudominio.com;

# Recargar Nginx
nginx -t && systemctl reload nginx
```

#### Activar HTTPS/SSL gratuito (Let's Encrypt)

```bash
apt install certbot python3-certbot-nginx
certbot --nginx -d tudominio.com -d www.tudominio.com
# Renovación automática cada 90 días
certbot renew --dry-run
```

---

### Opción B: Railway (gratuito para empezar, sin tarjeta)

Railway detecta Flask automáticamente.

1. Ir a [railway.app](https://railway.app) → Sign in with GitHub
2. **New Project** → **Deploy from GitHub repo**
3. Seleccionar `logisteril-istul`
4. Railway detecta el `Procfile` automáticamente
5. En **Variables** agregar:
   ```
   SECRET_KEY = (generar en: python -c "import secrets; print(secrets.token_hex(32))")
   FLASK_ENV = production
   ```
6. En **Settings** → **Networking** → **Generate Domain** para obtener URL pública

---

### Opción C: Render (gratuito con limitaciones)

1. Ir a [render.com](https://render.com) → New → **Web Service**
2. Conectar repositorio GitHub `logisteril-istul`
3. Configurar:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn "app:create_app()" --bind 0.0.0.0:$PORT`
4. Variables de entorno: `SECRET_KEY`, `FLASK_ENV=production`

---

## PARTE 3 — Base de datos en producción

### SQLite (más simple, recomendado para empezar)

No requiere configuración adicional. El archivo `logisteril.db` se crea solo.

```bash
# En .env del servidor:
DATABASE_URL=sqlite:///logisteril.db
```

⚠️ **No usar SQLite en Railway/Render** — los archivos no persisten al reiniciar.

### PostgreSQL (recomendado para producción real)

```bash
# Instalar PostgreSQL en el VPS
sudo apt install postgresql postgresql-contrib

# Crear base de datos
sudo -u postgres psql
CREATE DATABASE logisteril;
CREATE USER logisteril_user WITH PASSWORD 'tu_contraseña_segura';
GRANT ALL PRIVILEGES ON DATABASE logisteril TO logisteril_user;
\q

# En .env del servidor:
DATABASE_URL=postgresql://logisteril_user:tu_contraseña_segura@localhost:5432/logisteril

# Agregar psycopg2 a requirements.txt
echo "psycopg2-binary==2.9.9" >> requirements.txt
pip install psycopg2-binary
```

---

## Resumen del flujo de trabajo

```
Computadora local          GitHub                Servidor VPS
─────────────────          ──────                ────────────
Editar código       →  git push  →  git pull + restart
      ↑                                      ↓
   git pull   ←     git push    ←    (nunca editar directo)
```

---

**ISTUL — Instituto Superior Tecnológico Universitario de Latacunga**
