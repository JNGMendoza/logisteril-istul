from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required
from models.database import db
from models.equipo import Equipo, Mantenimiento
from utils.permisos import requiere_permiso
from datetime import datetime, date

equipos_bp = Blueprint('equipos', __name__, url_prefix='/equipos')

TIPOS = ['Autoclave', 'Termoselladora', 'Lavadora ultrasónica', 'Lavadora automática',
         'Secadora', 'Esterilizador EO', 'Plasma', 'Otro']
ESTADOS = ['operativo', 'mantenimiento', 'fuera_servicio']

@equipos_bp.route('/')
@login_required
@requiere_permiso('equipos')
def index():
    estado = request.args.get('estado', '')
    tipo   = request.args.get('tipo', '')
    query  = Equipo.query.filter_by(activo=True)
    if estado:
        query = query.filter_by(estado=estado)
    if tipo:
        query = query.filter_by(tipo=tipo)
    equipos = query.order_by(Equipo.nombre).all()

    # Alertas de calibración (próximos 30 días)
    limite = date.today()
    alertas_cal = [e for e in equipos
                   if e.fecha_proxima_calibracion and e.fecha_proxima_calibracion <= limite]

    return render_template('equipos/index.html',
        equipos=equipos, tipos=TIPOS, estados=ESTADOS,
        estado_sel=estado, tipo_sel=tipo, alertas_cal=alertas_cal
    )

@equipos_bp.route('/nuevo', methods=['GET', 'POST'])
@login_required
@requiere_permiso('equipos')
def nuevo():
    if request.method == 'POST':
        equipo = Equipo(
            nombre              = request.form['nombre'],
            tipo                = request.form['tipo'],
            marca               = request.form.get('marca', ''),
            modelo              = request.form.get('modelo', ''),
            numero_serie        = request.form.get('numero_serie', '') or None,
            ubicacion           = request.form.get('ubicacion', ''),
            estado              = request.form.get('estado', 'operativo'),
            fecha_adquisicion   = _parse_date(request.form.get('fecha_adquisicion')),
            fecha_ultima_calibracion  = _parse_date(request.form.get('fecha_ultima_calibracion')),
            fecha_proxima_calibracion = _parse_date(request.form.get('fecha_proxima_calibracion')),
            observaciones       = request.form.get('observaciones', ''),
        )
        db.session.add(equipo)
        db.session.commit()
        flash(f'Equipo "{equipo.nombre}" registrado.', 'success')
        return redirect(url_for('equipos.index'))

    return render_template('equipos/form.html', equipo=None, tipos=TIPOS, estados=ESTADOS)

@equipos_bp.route('/editar/<int:id>', methods=['GET', 'POST'])
@login_required
@requiere_permiso('equipos')
def editar(id):
    equipo = Equipo.query.get_or_404(id)
    if request.method == 'POST':
        equipo.nombre     = request.form['nombre']
        equipo.tipo       = request.form['tipo']
        equipo.marca      = request.form.get('marca', '')
        equipo.modelo     = request.form.get('modelo', '')
        equipo.ubicacion  = request.form.get('ubicacion', '')
        equipo.estado     = request.form.get('estado', equipo.estado)
        equipo.fecha_ultima_calibracion  = _parse_date(request.form.get('fecha_ultima_calibracion'))
        equipo.fecha_proxima_calibracion = _parse_date(request.form.get('fecha_proxima_calibracion'))
        equipo.observaciones = request.form.get('observaciones', '')
        db.session.commit()
        flash('Equipo actualizado.', 'success')
        return redirect(url_for('equipos.index'))

    return render_template('equipos/form.html', equipo=equipo, tipos=TIPOS, estados=ESTADOS)

@equipos_bp.route('/mantenimiento/<int:id>', methods=['GET', 'POST'])
@login_required
@requiere_permiso('equipos')
def mantenimiento(id):
    equipo = Equipo.query.get_or_404(id)
    if request.method == 'POST':
        mant = Mantenimiento(
            equipo_id           = equipo.id,
            tipo                = request.form['tipo'],
            descripcion         = request.form['descripcion'],
            tecnico_responsable = request.form.get('tecnico_responsable', ''),
            costo               = float(request.form.get('costo', 0) or 0),
            fecha               = _parse_date(request.form['fecha']) or date.today(),
            proximo_mantenimiento = _parse_date(request.form.get('proximo_mantenimiento')),
        )
        # Si es calibración, actualizar fechas del equipo
        if mant.tipo == 'calibracion':
            equipo.fecha_ultima_calibracion  = mant.fecha
            equipo.fecha_proxima_calibracion = mant.proximo_mantenimiento

        db.session.add(mant)
        db.session.commit()
        flash('Mantenimiento registrado.', 'success')
        return redirect(url_for('equipos.index'))

    return render_template('equipos/mantenimiento.html', equipo=equipo)

def _parse_date(value):
    if not value:
        return None
    try:
        return datetime.strptime(value, '%Y-%m-%d').date()
    except (ValueError, TypeError):
        return None
