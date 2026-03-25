from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from models.database import db
from models.usuario import Usuario, ROLES
from utils.permisos import requiere_permiso, solo_admin

usuarios_bp = Blueprint('usuarios', __name__, url_prefix='/usuarios')

@usuarios_bp.route('/')
@login_required
@requiere_permiso('usuarios')
def index():
    usuarios = Usuario.query.order_by(Usuario.activo.desc(), Usuario.nombre).all()
    return render_template('usuarios/index.html', usuarios=usuarios, roles=ROLES)

@usuarios_bp.route('/nuevo', methods=['GET', 'POST'])
@login_required
@solo_admin
def nuevo():
    if request.method == 'POST':
        if Usuario.query.filter_by(username=request.form['username']).first():
            flash('El nombre de usuario ya existe.', 'danger')
            return render_template('usuarios/form.html', usuario=None, roles=ROLES)

        u = Usuario(
            username = request.form['username'],
            nombre   = request.form['nombre'],
            apellido = request.form['apellido'],
            email    = request.form['email'],
            rol      = request.form.get('rol', 'tecnico'),
            activo   = True,
        )
        password = request.form.get('password', '')
        if len(password) < 8:
            flash('La contraseña debe tener mínimo 8 caracteres.', 'danger')
            return render_template('usuarios/form.html', usuario=None, roles=ROLES)

        u.set_password(password)
        db.session.add(u)
        db.session.commit()
        flash(f'Usuario {u.username} creado correctamente.', 'success')
        return redirect(url_for('usuarios.index'))

    return render_template('usuarios/form.html', usuario=None, roles=ROLES)

@usuarios_bp.route('/editar/<int:id>', methods=['GET', 'POST'])
@login_required
@solo_admin
def editar(id):
    u = Usuario.query.get_or_404(id)
    if request.method == 'POST':
        u.nombre   = request.form.get('nombre', u.nombre)
        u.apellido = request.form.get('apellido', u.apellido)
        u.email    = request.form.get('email', u.email)
        u.rol      = request.form.get('rol', u.rol)
        u.activo   = 'activo' in request.form

        nueva_pw = request.form.get('password', '')
        if nueva_pw:
            if len(nueva_pw) < 8:
                flash('La contraseña debe tener mínimo 8 caracteres.', 'danger')
                return render_template('usuarios/form.html', usuario=u, roles=ROLES)
            u.set_password(nueva_pw)

        db.session.commit()
        flash(f'Usuario {u.username} actualizado.', 'success')
        return redirect(url_for('usuarios.index'))

    return render_template('usuarios/form.html', usuario=u, roles=ROLES)

@usuarios_bp.route('/desactivar/<int:id>', methods=['POST'])
@login_required
@solo_admin
def desactivar(id):
    u = Usuario.query.get_or_404(id)
    if u.id == current_user.id:
        flash('No puedes desactivar tu propia cuenta.', 'danger')
        return redirect(url_for('usuarios.index'))
    u.activo = not u.activo
    db.session.commit()
    estado = 'activado' if u.activo else 'desactivado'
    flash(f'Usuario {u.username} {estado}.', 'info')
    return redirect(url_for('usuarios.index'))
