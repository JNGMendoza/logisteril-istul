from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from models.database import db
from models.ciclo import Ciclo
from models.equipo import Equipo
from utils.permisos import requiere_permiso
from datetime import datetime

ciclos_bp = Blueprint('ciclos', __name__, url_prefix='/ciclos')

METODOS = ['vapor', 'EO', 'plasma', 'calor_seco']
SERVICIOS = ['Quirófano', 'UCI', 'Urgencias', 'Pediatría', 'Ginecología',
             'Traumatología', 'Odontología', 'Endoscopía', 'Otro']

def generar_numero_ciclo():
    """Genera número único: CIC-YYYYMM-NNNN"""
    prefijo = datetime.utcnow().strftime('CIC-%Y%m-')
    ultimo = Ciclo.query.filter(
        Ciclo.numero_ciclo.like(f'{prefijo}%')
    ).order_by(Ciclo.id.desc()).first()
    if ultimo:
        n = int(ultimo.numero_ciclo.split('-')[-1]) + 1
    else:
        n = 1
    return f'{prefijo}{n:04d}'

@ciclos_bp.route('/')
@login_required
@requiere_permiso('ciclos')
def index():
    resultado = request.args.get('resultado', '')
    metodo    = request.args.get('metodo', '')
    buscar    = request.args.get('buscar', '')
    fecha_desde = request.args.get('fecha_desde', '')
    fecha_hasta = request.args.get('fecha_hasta', '')

    query = Ciclo.query
    if resultado:
        query = query.filter_by(resultado=resultado)
    if metodo:
        query = query.filter_by(metodo=metodo)
    if buscar:
        query = query.filter(
            Ciclo.numero_ciclo.ilike(f'%{buscar}%') |
            Ciclo.contenido.ilike(f'%{buscar}%') |
            Ciclo.servicio_destino.ilike(f'%{buscar}%')
        )
    if fecha_desde:
        try:
            fd = datetime.strptime(fecha_desde, '%Y-%m-%d')
            query = query.filter(Ciclo.fecha_inicio >= fd)
        except ValueError:
            pass
    if fecha_hasta:
        try:
            fh = datetime.strptime(fecha_hasta, '%Y-%m-%d')
            query = query.filter(Ciclo.fecha_inicio <= fh)
        except ValueError:
            pass

    ciclos = query.order_by(Ciclo.fecha_inicio.desc()).all()
    return render_template('ciclos/index.html',
        ciclos=ciclos, metodos=METODOS, resultado_sel=resultado,
        metodo_sel=metodo, buscar=buscar, fecha_desde=fecha_desde, fecha_hasta=fecha_hasta
    )

@ciclos_bp.route('/nuevo', methods=['GET', 'POST'])
@login_required
@requiere_permiso('ciclos')
def nuevo():
    equipos = Equipo.query.filter_by(activo=True, estado='operativo').all()
    if request.method == 'POST':
        ciclo = Ciclo(
            numero_ciclo     = generar_numero_ciclo(),
            equipo_id        = int(request.form['equipo_id']),
            usuario_id       = current_user.id,
            metodo           = request.form['metodo'],
            temperatura      = float(request.form.get('temperatura', 0) or 0),
            presion          = float(request.form.get('presion', 0) or 0),
            tiempo_minutos   = int(request.form.get('tiempo_minutos', 0) or 0),
            contenido        = request.form['contenido'],
            servicio_destino = request.form.get('servicio_destino', ''),
            lote             = request.form.get('lote', ''),
            indicador_quimico   = request.form.get('indicador_quimico', 'pendiente'),
            indicador_biologico = request.form.get('indicador_biologico', 'pendiente'),
            resultado        = request.form.get('resultado', 'en_proceso'),
            observaciones    = request.form.get('observaciones', ''),
        )
        if ciclo.resultado == 'aprobado':
            ciclo.fecha_fin = datetime.utcnow()

        db.session.add(ciclo)
        db.session.commit()
        flash(f'Ciclo {ciclo.numero_ciclo} registrado.', 'success')
        return redirect(url_for('ciclos.index'))

    return render_template('ciclos/form.html', ciclo=None,
                           equipos=equipos, metodos=METODOS, servicios=SERVICIOS)

@ciclos_bp.route('/editar/<int:id>', methods=['GET', 'POST'])
@login_required
@requiere_permiso('ciclos')
def editar(id):
    ciclo   = Ciclo.query.get_or_404(id)
    equipos = Equipo.query.filter_by(activo=True).all()
    if request.method == 'POST':
        ciclo.metodo           = request.form.get('metodo', ciclo.metodo)
        ciclo.temperatura      = float(request.form.get('temperatura', 0) or 0)
        ciclo.presion          = float(request.form.get('presion', 0) or 0)
        ciclo.tiempo_minutos   = int(request.form.get('tiempo_minutos', 0) or 0)
        ciclo.contenido        = request.form.get('contenido', ciclo.contenido)
        ciclo.servicio_destino = request.form.get('servicio_destino', '')
        ciclo.indicador_quimico   = request.form.get('indicador_quimico', ciclo.indicador_quimico)
        ciclo.indicador_biologico = request.form.get('indicador_biologico', ciclo.indicador_biologico)
        ciclo.resultado        = request.form.get('resultado', ciclo.resultado)
        ciclo.observaciones    = request.form.get('observaciones', '')
        if ciclo.resultado == 'aprobado' and not ciclo.fecha_fin:
            ciclo.fecha_fin = datetime.utcnow()
        db.session.commit()
        flash('Ciclo actualizado.', 'success')
        return redirect(url_for('ciclos.index'))

    return render_template('ciclos/form.html', ciclo=ciclo,
                           equipos=equipos, metodos=METODOS, servicios=SERVICIOS)

@ciclos_bp.route('/ver/<int:id>')
@login_required
@requiere_permiso('ciclos')
def ver(id):
    ciclo = Ciclo.query.get_or_404(id)
    return render_template('ciclos/ver.html', ciclo=ciclo)
