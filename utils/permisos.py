from functools import wraps
from flask import abort, flash, redirect, url_for
from flask_login import current_user

def requiere_permiso(modulo):
    """Decorador que verifica si el usuario tiene permiso para el módulo."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.tiene_permiso(modulo):
                flash('No tienes permisos para acceder a esta sección.', 'danger')
                return redirect(url_for('dashboard.index'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def solo_admin(f):
    """Decorador que permite acceso solo al administrador."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.rol != 'admin':
            flash('Esta acción requiere privilegios de administrador.', 'danger')
            return redirect(url_for('dashboard.index'))
        return f(*args, **kwargs)
    return decorated_function
