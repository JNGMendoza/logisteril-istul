from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from models.database import db
from models.usuario import Usuario
from datetime import datetime

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        remember = request.form.get('remember', False)

        usuario = Usuario.query.filter_by(username=username).first()

        if usuario and usuario.check_password(password):
            if not usuario.activo:
                flash('Tu cuenta está desactivada. Contacta al administrador.', 'danger')
                return render_template('auth/login.html')

            login_user(usuario, remember=remember)
            usuario.ultimo_login = datetime.utcnow()
            db.session.commit()

            next_page = request.args.get('next')
            flash(f'Bienvenido/a, {usuario.nombre_completo}!', 'success')
            return redirect(next_page or url_for('dashboard.index'))
        else:
            flash('Usuario o contraseña incorrectos.', 'danger')

    return render_template('auth/login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Sesión cerrada correctamente.', 'info')
    return redirect(url_for('auth.login'))

@auth_bp.route('/perfil', methods=['GET', 'POST'])
@login_required
def perfil():
    if request.method == 'POST':
        current_user.nombre   = request.form.get('nombre', current_user.nombre)
        current_user.apellido = request.form.get('apellido', current_user.apellido)
        current_user.email    = request.form.get('email', current_user.email)

        nueva_pw = request.form.get('nueva_password', '')
        if nueva_pw:
            if len(nueva_pw) < 8:
                flash('La contraseña debe tener al menos 8 caracteres.', 'danger')
                return render_template('auth/perfil.html')
            current_user.set_password(nueva_pw)

        db.session.commit()
        flash('Perfil actualizado correctamente.', 'success')
        return redirect(url_for('auth.perfil'))

    return render_template('auth/perfil.html')
