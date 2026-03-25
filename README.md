# LogiSteril ISTUL
## Plataforma de Logística para Central de Esterilización

Sistema de gestión integral para la Central de Esterilización del ISTUL.
Desarrollado en **Python 3 + Flask + SQLite/PostgreSQL**.

---

## Módulos incluidos

| Módulo | Descripción |
|--------|-------------|
| **Login y roles** | Autenticación segura con 3 roles: Administrador, Supervisor, Técnico |
| **Inventario** | Control de insumos, entradas/salidas, alertas de stock mínimo |
| **Equipos** | Registro de equipos, calibraciones y mantenimientos |
| **Ciclos** | Trazabilidad completa de ciclos de esterilización |
| **Reportes** | Reportes de inventario, ciclos y equipos imprimibles |
| **Usuarios** | Gestión de usuarios y permisos (solo Admin) |

---

## Instalación rápida

### Requisitos
- Python 3.9 o superior
- pip

### Pasos

```bash
# 1. Descomprimir el proyecto
unzip logisteril.zip
cd logisteril

# 2. Crear entorno virtual (recomendado)
python -m venv venv

# Windows:
venv\Scripts\activate

# Linux/Mac:
source venv/bin/activate

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Ejecutar la aplicación
python app.py
```

### 5. Abrir en el navegador
```
http://localhost:5000
```

---

## Credenciales de prueba

| Usuario | Contraseña | Rol | Permisos |
|---------|-----------|-----|----------|
| `admin` | `Admin1234!` | Administrador | Acceso total |
| `supervisor` | `Super1234!` | Supervisor | Sin gestión de usuarios |
| `tecnico` | `Tecnico1234!` | Técnico | Inventario, equipos y ciclos |

> **Importante:** Cambia las contraseñas antes de usar en producción.

---

## Variables de entorno (producción)

```bash
# Clave secreta segura
SECRET_KEY=tu-clave-secreta-muy-larga

# Base de datos PostgreSQL (opcional, por defecto usa SQLite)
DATABASE_URL=postgresql://usuario:password@localhost/logisteril
```

---

## Estructura del proyecto

```
logisteril/
├── app.py                  # Punto de entrada principal
├── requirements.txt        # Dependencias Python
├── models/
│   ├── database.py         # Inicialización BD + datos de ejemplo
│   ├── usuario.py          # Modelo de usuarios y roles
│   ├── insumo.py           # Modelo de insumos e inventario
│   ├── equipo.py           # Modelo de equipos y mantenimientos
│   └── ciclo.py            # Modelo de ciclos de esterilización
├── routes/
│   ├── auth.py             # Login, logout, perfil
│   ├── dashboard.py        # Dashboard con KPIs
│   ├── inventario.py       # CRUD inventario + movimientos
│   ├── equipos.py          # CRUD equipos + mantenimientos
│   ├── ciclos.py           # CRUD ciclos de esterilización
│   ├── reportes.py         # Reportes imprimibles
│   └── usuarios.py         # Gestión de usuarios (admin)
├── templates/
│   ├── base.html           # Layout principal con sidebar
│   ├── auth/               # Login y perfil
│   ├── dashboard/          # Dashboard principal
│   ├── inventario/         # Listado, formularios, movimientos
│   ├── equipos/            # Listado, formularios, mantenimientos
│   ├── ciclos/             # Listado, formularios, detalle
│   ├── reportes/           # Reportes imprimibles
│   └── usuarios/           # Gestión de usuarios
└── utils/
    ├── permisos.py         # Decoradores de control de acceso
    └── context.py          # Variables globales para templates
```

---

## Tecnologías usadas

- **Backend:** Python 3 + Flask 3.0
- **ORM / BD:** SQLAlchemy + SQLite (dev) / PostgreSQL (prod)
- **Frontend:** Bootstrap 5.3 + Bootstrap Icons + Chart.js
- **Auth:** Flask-Login + Werkzeug (bcrypt)

---

## Próximas mejoras sugeridas

- Exportación a PDF con WeasyPrint o ReportLab
- Notificaciones por correo (Flask-Mail) para alertas de stock
- API REST para integración con otros sistemas hospitalarios
- Módulo de trazabilidad con código QR por paquete
- Backup automático de la base de datos

---

**ISTUL — Instituto Superior Tecnológico Universitario de Latacunga**
