# Guía de despliegue en Render
## LogiSteril ISTUL

---

## Requisitos previos
- Cuenta en [GitHub](https://github.com) ✅
- Código subido a un repositorio GitHub ✅
- Cuenta en [Render](https://render.com) (gratuita)

---

## PASO 1 — Subir el código a GitHub

Si aún no lo has hecho:

```bash
cd logisteril

git init
git add .
git commit -m "feat: LogiSteril ISTUL - versión inicial"

# Crear el repositorio en github.com primero, luego:
git remote add origin https://github.com/TU_USUARIO/logisteril-istul.git
git branch -M main
git push -u origin main
```

---

## PASO 2 — Crear cuenta en Render

1. Ir a [render.com](https://render.com)
2. Clic en **"Get Started for Free"**
3. Registrarse con tu cuenta de **GitHub** (más fácil)

---

## PASO 3 — Crear la base de datos PostgreSQL

⚠️ Hacer esto **PRIMERO**, antes del servicio web.

1. En el dashboard de Render → **"New +"** → **"PostgreSQL"**
2. Configurar:
   - **Name:** `logisteril-db`
   - **Database:** `logisteril`
   - **User:** `logisteril_user`
   - **Region:** Oregon (US West) — o la más cercana
   - **Plan:** **Free** ✅
3. Clic **"Create Database"**
4. Esperar ~2 minutos a que se cree
5. En la página de la BD, copiar el valor de **"Internal Database URL"** — lo necesitarás en el paso 4

---

## PASO 4 — Crear el servicio web

1. En el dashboard → **"New +"** → **"Web Service"**
2. Conectar repositorio:
   - Clic **"Connect account"** (conectar GitHub si no lo has hecho)
   - Buscar y seleccionar `logisteril-istul`
   - Clic **"Connect"**
3. Configurar el servicio:

   | Campo | Valor |
   |-------|-------|
   | **Name** | `logisteril-istul` |
   | **Region** | Oregon (igual que la BD) |
   | **Branch** | `main` |
   | **Runtime** | `Python 3` |
   | **Build Command** | `pip install -r requirements.txt` |
   | **Start Command** | `gunicorn "app:create_app()" --bind 0.0.0.0:$PORT --workers 2 --timeout 120` |
   | **Plan** | **Free** ✅ |

4. Bajar a la sección **"Environment Variables"** y agregar:

   | Key | Value |
   |-----|-------|
   | `SECRET_KEY` | (clic en "Generate" para generar una clave segura automáticamente) |
   | `FLASK_ENV` | `production` |
   | `DATABASE_URL` | (pegar la "Internal Database URL" del paso 3) |

5. Clic **"Create Web Service"**

---

## PASO 5 — Esperar el despliegue

Render ejecutará automáticamente:
```
==> pip install -r requirements.txt
==> gunicorn "app:create_app()" ...
```

Verás los logs en tiempo real. Al finalizar verás:
```
✅ BD inicializada con datos de ejemplo.
[INFO] Listening at: http://0.0.0.0:10000
```

⏱️ El primer despliegue tarda ~3-5 minutos.

---

## PASO 6 — Abrir la aplicación

En la parte superior del servicio verás la URL pública:
```
https://logisteril-istul.onrender.com
```

Inicia sesión con:
- Usuario: `admin` / Contraseña: `Admin1234!`

---

## ⚠️ Limitaciones del plan gratuito de Render

| Limitación | Detalle |
|------------|---------|
| **Sleep automático** | El servicio se "duerme" tras 15 min sin visitas. La primera visita tarda ~30 seg en despertar. |
| **Base de datos** | El plan Free de PostgreSQL expira a los **90 días**. Después hay que pagar ~$7/mes o migrar a otro plan. |
| **Horas de cómputo** | 750 horas/mes gratis (suficiente para uso continuo en un solo servicio). |

### Solución al sleep: mantener activo
Para evitar que se duerma, puedes usar [UptimeRobot](https://uptimerobot.com) (gratuito):
1. Crear cuenta en uptimerobot.com
2. **"Add New Monitor"** → HTTP(s)
3. URL: `https://logisteril-istul.onrender.com`
4. Intervalo: cada **5 minutos**
Esto hace un ping cada 5 minutos y mantiene el servicio activo.

---

## Actualizar el sistema (deploys futuros)

Cada vez que hagas `git push` a GitHub, Render **redespliega automáticamente**:

```bash
# En tu PC, después de hacer cambios:
git add .
git commit -m "descripción del cambio"
git push

# Render detecta el push y redespliega solo ✅
```

Puedes ver el historial de deploys en Render → tu servicio → pestaña **"Deploys"**.

---

## Ver logs en Render

Si algo falla, los logs están en:
- Render → tu servicio → pestaña **"Logs"**

Errores comunes:
- `ModuleNotFoundError` → falta algún paquete en `requirements.txt`
- `sqlalchemy.exc.OperationalError` → verificar que `DATABASE_URL` esté bien configurado
- Puerto incorrecto → el `Start Command` debe usar `$PORT` (ya está configurado)

---

## Estructura de archivos relevantes para Render

```
logisteril/
├── requirements.txt   ← Render instala estas dependencias
├── Procfile           ← Render usa este comando para iniciar
├── render.yaml        ← Configuración automática (opcional)
└── app.py             ← create_app() es el punto de entrada
```

---

**ISTUL — Instituto Superior Tecnológico Universitario de Latacunga**
