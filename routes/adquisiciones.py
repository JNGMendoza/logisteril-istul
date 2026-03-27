from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from models.database import db
from models.adquisicion import Adquisicion, AREAS_PRACTICA
from models.insumo import Insumo, MovimientoInventario
from models.usuario import Usuario
from utils.permisos import requiere_permiso
from datetime import datetime, timedelta
from sqlalchemy import func

adquisiciones_bp = Blueprint('adquisiciones', __name__, url_prefix='/adquisiciones')


@adquisiciones_bp.route('/')
@login_required
@requiere_permiso('adquisiciones')
def index():
    buscar   = request.args.get('buscar', '')
    area     = request.args.get('area', '')
    fecha_d  = request.args.get('fecha_desde', '')
    fecha_h  = request.args.get('fecha_hasta', '')
    insumo_f = request.args.get('insumo_id', '')

    query = Adquisicion.query
    if buscar:
        query = query.filter(
            Adquisicion.solicitante_nombre.ilike(f'%{buscar}%') |
            Adquisicion.solicitante_cedula.ilike(f'%{buscar}%') |
            Adquisicion.solicitante_codigo.ilike(f'%{buscar}%') |
            Adquisicion.motivo.ilike(f'%{buscar}%')
        )
    if area:
        query = query.filter_by(area_practica=area)
    if insumo_f:
        query = query.filter_by(insumo_id=int(insumo_f))
    if fecha_d:
        try:
            query = query.filter(Adquisicion.fecha >= datetime.strptime(fecha_d, '%Y-%m-%d'))
        except ValueError:
            pass
    if fecha_h:
        try:
            query = query.filter(Adquisicion.fecha <= datetime.strptime(fecha_h, '%Y-%m-%d'))
        except ValueError:
            pass

    adquisiciones = query.order_by(Adquisicion.fecha.desc()).all()
    insumos       = Insumo.query.filter_by(activo=True).order_by(Insumo.nombre).all()

    return render_template('adquisiciones/index.html',
        adquisiciones=adquisiciones,
        areas=AREAS_PRACTICA,
        insumos=insumos,
        buscar=buscar, area_sel=area,
        fecha_desde=fecha_d, fecha_hasta=fecha_h,
        insumo_sel=insumo_f,
    )


@adquisiciones_bp.route('/nueva', methods=['GET', 'POST'])
@login_required
@requiere_permiso('adquisiciones')
def nueva():
    insumos     = Insumo.query.filter_by(activo=True).order_by(Insumo.nombre).all()
    estudiantes = Usuario.query.filter_by(rol='estudiante', activo=True)\
                               .order_by(Usuario.apellido).all()

    if request.method == 'POST':
        insumo_id = int(request.form['insumo_id'])
        cantidad  = float(request.form['cantidad'])
        insumo    = Insumo.query.get_or_404(insumo_id)

        if cantidad > insumo.stock_actual:
            flash(f'Stock insuficiente. Disponible: {insumo.stock_actual} {insumo.unidad}', 'danger')
            return render_template('adquisiciones/nueva.html',
                                   insumos=insumos, estudiantes=estudiantes, areas=AREAS_PRACTICA)

        estudiante_id = request.form.get('estudiante_id') or None
        if estudiante_id:
            estudiante_id = int(estudiante_id)
            est = Usuario.query.get(estudiante_id)
            nombre   = est.nombre_completo
            cedula   = est.cedula or ''
            codigo   = est.codigo_estudiante or ''
            carrera  = est.carrera or ''
            semestre = est.semestre or ''
        else:
            nombre   = request.form.get('solicitante_nombre', '').strip()
            cedula   = request.form.get('solicitante_cedula', '').strip()
            codigo   = request.form.get('solicitante_codigo', '').strip()
            carrera  = request.form.get('solicitante_carrera', '').strip()
            semestre = request.form.get('solicitante_semestre', '').strip()

        if not nombre and not estudiante_id:
            flash('Debes ingresar el nombre del estudiante.', 'danger')
            return render_template('adquisiciones/nueva.html',
                                   insumos=insumos, estudiantes=estudiantes, areas=AREAS_PRACTICA)

        adq = Adquisicion(
            estudiante_id        = estudiante_id,
            solicitante_nombre   = nombre   if not estudiante_id else None,
            solicitante_cedula   = cedula   if not estudiante_id else None,
            solicitante_codigo   = codigo   if not estudiante_id else None,
            solicitante_carrera  = carrera  if not estudiante_id else None,
            solicitante_semestre = semestre if not estudiante_id else None,
            area_practica        = request.form['area_practica'],
            insumo_id            = insumo_id,
            cantidad             = cantidad,
            motivo               = request.form['motivo'],
            tecnico_id           = current_user.id,
            observaciones        = request.form.get('observaciones', ''),
        )

        stock_antes = insumo.stock_actual
        insumo.stock_actual -= cantidad

        mov = MovimientoInventario(
            insumo_id     = insumo_id,
            usuario_id    = current_user.id,
            tipo          = 'salida',
            cantidad      = cantidad,
            stock_antes   = stock_antes,
            stock_despues = insumo.stock_actual,
            motivo        = f'Entrega a {adq.nombre_solicitante} — {adq.motivo}',
        )

        db.session.add(adq)
        db.session.add(mov)
        db.session.commit()

        flash(f'Entrega registrada correctamente a {adq.nombre_solicitante}.', 'success')
        return redirect(url_for('adquisiciones.index'))

    return render_template('adquisiciones/nueva.html',
                           insumos=insumos, estudiantes=estudiantes, areas=AREAS_PRACTICA)


@adquisiciones_bp.route('/mis-solicitudes')
@login_required
def mis_solicitudes():
    if not current_user.tiene_permiso('mis_solicitudes') and \
       not current_user.tiene_permiso('adquisiciones'):
        flash('No tienes permiso para ver esta sección.', 'danger')
        return redirect(url_for('dashboard.index'))

    if current_user.es_estudiante:
        adqs = Adquisicion.query\
            .filter_by(estudiante_id=current_user.id)\
            .order_by(Adquisicion.fecha.desc()).all()
    else:
        adqs = Adquisicion.query.order_by(Adquisicion.fecha.desc()).limit(50).all()

    return render_template('adquisiciones/mis_solicitudes.html', adquisiciones=adqs)


@adquisiciones_bp.route('/buscar-estudiante')
@login_required
def buscar_estudiante():
    q = request.args.get('q', '').strip()
    if len(q) < 2:
        return jsonify([])
    estudiantes = Usuario.query.filter(
        Usuario.rol == 'estudiante',
        Usuario.activo == True,
        (Usuario.cedula.ilike(f'%{q}%')) |
        (Usuario.codigo_estudiante.ilike(f'%{q}%')) |
        (Usuario.nombre.ilike(f'%{q}%')) |
        (Usuario.apellido.ilike(f'%{q}%'))
    ).limit(10).all()
    return jsonify([{
        'id':       e.id,
        'nombre':   e.nombre_completo,
        'cedula':   e.cedula or '',
        'codigo':   e.codigo_estudiante or '',
        'carrera':  e.carrera or '',
        'semestre': e.semestre or '',
    } for e in estudiantes])


@adquisiciones_bp.route('/reporte')
@login_required
@requiere_permiso('adquisiciones')
def reporte():
    desde      = request.args.get('desde', '')
    hasta      = request.args.get('hasta', '')
    buscar_est = request.args.get('buscar_est', '')
    area_sel   = request.args.get('area', '')

    fi = datetime.utcnow() - timedelta(days=30)
    ff = datetime.utcnow()
    if desde:
        try:
            fi = datetime.strptime(desde, '%Y-%m-%d')
        except ValueError:
            pass
    if hasta:
        try:
            ff = datetime.strptime(hasta, '%Y-%m-%d')
        except ValueError:
            pass

    query = Adquisicion.query.filter(Adquisicion.fecha.between(fi, ff))
    if area_sel:
        query = query.filter_by(area_practica=area_sel)

    adqs = query.order_by(Adquisicion.fecha.desc()).all()

    # Filtrar por estudiante si se escribió búsqueda
    if buscar_est:
        buscar_lower = buscar_est.lower()
        adqs = [a for a in adqs if
                buscar_lower in a.nombre_solicitante.lower() or
                buscar_lower in (a.cedula_solicitante or '').lower() or
                (a.estudiante and buscar_lower in (a.estudiante.codigo_estudiante or '').lower())]

    total_entregas    = len(adqs)
    total_unidades    = round(sum(a.cantidad for a in adqs), 2)
    insumos_distintos = len(set(a.insumo_id for a in adqs))
    estudiantes_unicos = len(set(a.nombre_solicitante for a in adqs))

    # Top insumos
    top_insumos = db.session.query(
        Insumo.nombre,
        func.sum(Adquisicion.cantidad).label('total'),
        func.count(Adquisicion.id).label('veces')
    ).join(Adquisicion).filter(
        Adquisicion.fecha.between(fi, ff)
    ).group_by(Insumo.id).order_by(func.sum(Adquisicion.cantidad).desc()).limit(5).all()

    # Por área
    por_area = db.session.query(
        Adquisicion.area_practica,
        func.count(Adquisicion.id).label('total')
    ).filter(
        Adquisicion.fecha.between(fi, ff)
    ).group_by(Adquisicion.area_practica)\
     .order_by(func.count(Adquisicion.id).desc()).all()

    # Top estudiantes
    conteo_est = {}
    for a in adqs:
        nombre = a.nombre_solicitante
        conteo_est[nombre] = conteo_est.get(nombre, 0) + 1
    top_estudiantes = sorted(conteo_est.items(), key=lambda x: x[1], reverse=True)[:5]

    # Detalle agrupado por estudiante (expandible)
    est_dict = {}
    for a in adqs:
        clave = a.nombre_solicitante
        if clave not in est_dict:
            est_dict[clave] = {
                'nombre':        a.nombre_solicitante,
                'cedula':        a.cedula_solicitante,
                'carrera':       a.carrera_solicitante,
                'adquisiciones': [],
                'total_retiros': 0,
                'total_unidades': 0.0,
            }
        est_dict[clave]['adquisiciones'].append(a)
        est_dict[clave]['total_retiros']  += 1
        est_dict[clave]['total_unidades'] += a.cantidad

    estudiantes_detalle = sorted(
        est_dict.values(),
        key=lambda x: x['total_retiros'],
        reverse=True
    )

    return render_template('adquisiciones/reporte.html',
        adqs=adqs,
        total_entregas=total_entregas,
        total_unidades=total_unidades,
        estudiantes_unicos=estudiantes_unicos,
        insumos_distintos=insumos_distintos,
        top_insumos=top_insumos,
        por_area=por_area,
        top_estudiantes=top_estudiantes,
        estudiantes_detalle=estudiantes_detalle,
        areas=AREAS_PRACTICA,
        area_sel=area_sel,
        buscar_est=buscar_est,
        fecha_inicio=fi,
        fecha_fin=ff,
        desde=desde,
        hasta=hasta,
        fecha=datetime.now(),
    )
