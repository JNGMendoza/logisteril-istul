from flask import Blueprint, render_template, request, make_response
from flask_login import login_required
from models.database import db
from models.insumo import Insumo, MovimientoInventario
from models.equipo import Equipo
from models.ciclo import Ciclo
from utils.permisos import requiere_permiso
from datetime import datetime, timedelta
from sqlalchemy import func

reportes_bp = Blueprint('reportes', __name__, url_prefix='/reportes')

@reportes_bp.route('/')
@login_required
@requiere_permiso('reportes')
def index():
    return render_template('reportes/index.html')

@reportes_bp.route('/inventario')
@login_required
@requiere_permiso('reportes')
def inventario():
    insumos = Insumo.query.filter_by(activo=True).order_by(Insumo.categoria, Insumo.nombre).all()
    criticos = [i for i in insumos if i.estado_stock in ('critico', 'sin_stock')]
    return render_template('reportes/inventario.html',
        insumos=insumos, criticos=criticos, fecha=datetime.now())

@reportes_bp.route('/ciclos')
@login_required
@requiere_permiso('reportes')
def ciclos():
    desde = request.args.get('desde', '')
    hasta = request.args.get('hasta', '')
    fecha_inicio = datetime.utcnow() - timedelta(days=30)
    fecha_fin    = datetime.utcnow()

    if desde:
        try: fecha_inicio = datetime.strptime(desde, '%Y-%m-%d')
        except ValueError: pass
    if hasta:
        try: fecha_fin = datetime.strptime(hasta, '%Y-%m-%d')
        except ValueError: pass

    ciclos = Ciclo.query.filter(
        Ciclo.fecha_inicio.between(fecha_inicio, fecha_fin)
    ).order_by(Ciclo.fecha_inicio.desc()).all()

    total        = len(ciclos)
    aprobados    = sum(1 for c in ciclos if c.resultado == 'aprobado')
    rechazados   = sum(1 for c in ciclos if c.resultado == 'rechazado')
    en_proceso   = sum(1 for c in ciclos if c.resultado == 'en_proceso')
    tasa_exito   = round(aprobados / total * 100, 1) if total > 0 else 0

    por_metodo   = {}
    for c in ciclos:
        por_metodo[c.metodo] = por_metodo.get(c.metodo, 0) + 1

    return render_template('reportes/ciclos.html',
        ciclos=ciclos, total=total, aprobados=aprobados,
        rechazados=rechazados, en_proceso=en_proceso,
        tasa_exito=tasa_exito, por_metodo=por_metodo,
        fecha_inicio=fecha_inicio, fecha_fin=fecha_fin,
        desde=desde, hasta=hasta, fecha=datetime.now()
    )

@reportes_bp.route('/equipos')
@login_required
@requiere_permiso('reportes')
def equipos():
    from datetime import date
    equipos = Equipo.query.filter_by(activo=True).order_by(Equipo.tipo, Equipo.nombre).all()
    hoy = date.today()
    vencidos = [e for e in equipos
                if e.fecha_proxima_calibracion and e.fecha_proxima_calibracion < hoy]
    proximos = [e for e in equipos
                if e.fecha_proxima_calibracion and
                hoy <= e.fecha_proxima_calibracion <= (hoy + timedelta(days=30))]
    return render_template('reportes/equipos.html',
        equipos=equipos, vencidos=vencidos, proximos=proximos, fecha=datetime.now())
