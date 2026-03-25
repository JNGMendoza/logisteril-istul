from flask import Blueprint, render_template
from flask_login import login_required
from models.database import db
from models.insumo import Insumo
from models.equipo import Equipo
from models.ciclo import Ciclo
from models.usuario import Usuario
from datetime import datetime, timedelta
from sqlalchemy import func

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/')
@dashboard_bp.route('/dashboard')
@login_required
def index():
    hoy = datetime.utcnow().date()
    hace_30_dias = datetime.utcnow() - timedelta(days=30)

    # KPIs inventario
    total_insumos   = Insumo.query.filter_by(activo=True).count()
    insumos_criticos = Insumo.query.filter(
        Insumo.activo == True,
        Insumo.stock_actual <= Insumo.stock_minimo
    ).count()

    # KPIs equipos
    total_equipos   = Equipo.query.filter_by(activo=True).count()
    equipos_op      = Equipo.query.filter_by(activo=True, estado='operativo').count()
    equipos_mant    = Equipo.query.filter_by(activo=True, estado='mantenimiento').count()

    # Equipos con calibración próxima (15 días)
    fecha_limite = hoy + timedelta(days=15)
    equipos_calibracion = Equipo.query.filter(
        Equipo.activo == True,
        Equipo.fecha_proxima_calibracion <= fecha_limite
    ).count()

    # KPIs ciclos
    ciclos_mes       = Ciclo.query.filter(Ciclo.fecha_inicio >= hace_30_dias).count()
    ciclos_aprobados = Ciclo.query.filter(
        Ciclo.fecha_inicio >= hace_30_dias,
        Ciclo.resultado == 'aprobado'
    ).count()
    ciclos_rechazados = Ciclo.query.filter(
        Ciclo.fecha_inicio >= hace_30_dias,
        Ciclo.resultado == 'rechazado'
    ).count()

    tasa_exito = round((ciclos_aprobados / ciclos_mes * 100), 1) if ciclos_mes > 0 else 0

    # Últimos ciclos
    ultimos_ciclos = Ciclo.query.order_by(Ciclo.fecha_inicio.desc()).limit(8).all()

    # Insumos con stock crítico
    alertas_stock = Insumo.query.filter(
        Insumo.activo == True,
        Insumo.stock_actual <= Insumo.stock_minimo
    ).order_by(Insumo.stock_actual).limit(5).all()

    # Ciclos por método (últimos 30 días)
    ciclos_por_metodo = db.session.query(
        Ciclo.metodo, func.count(Ciclo.id)
    ).filter(Ciclo.fecha_inicio >= hace_30_dias).group_by(Ciclo.metodo).all()

    return render_template('dashboard/index.html',
        total_insumos=total_insumos,
        insumos_criticos=insumos_criticos,
        total_equipos=total_equipos,
        equipos_op=equipos_op,
        equipos_mant=equipos_mant,
        equipos_calibracion=equipos_calibracion,
        ciclos_mes=ciclos_mes,
        ciclos_aprobados=ciclos_aprobados,
        ciclos_rechazados=ciclos_rechazados,
        tasa_exito=tasa_exito,
        ultimos_ciclos=ultimos_ciclos,
        alertas_stock=alertas_stock,
        ciclos_por_metodo=ciclos_por_metodo,
    )
