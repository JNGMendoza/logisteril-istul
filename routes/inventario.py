from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from models.database import db
from models.insumo import Insumo, MovimientoInventario
from utils.permisos import requiere_permiso
from datetime import datetime

inventario_bp = Blueprint('inventario', __name__, url_prefix='/inventario')

CATEGORIAS = ['Empaque', 'Indicadores', 'Limpieza', 'Esterilizante', 'Descartable', 'Otro']
UNIDADES   = ['Unidad', 'Caja', 'Rollo', 'Litro', 'Kilogramo', 'Metro', 'Ampolla', 'Paquete']

@inventario_bp.route('/')
@login_required
@requiere_permiso('inventario')
def index():
    categoria = request.args.get('categoria', '')
    estado    = request.args.get('estado', '')
    buscar    = request.args.get('buscar', '')

    query = Insumo.query.filter_by(activo=True)
    if categoria:
        query = query.filter_by(categoria=categoria)
    if buscar:
        query = query.filter(Insumo.nombre.ilike(f'%{buscar}%'))

    insumos = query.order_by(Insumo.nombre).all()

    if estado == 'critico':
        insumos = [i for i in insumos if i.estado_stock in ('critico', 'sin_stock')]
    elif estado == 'bajo':
        insumos = [i for i in insumos if i.estado_stock == 'bajo']

    return render_template('inventario/index.html',
        insumos=insumos,
        categorias=CATEGORIAS,
        categoria_sel=categoria,
        estado_sel=estado,
        buscar=buscar
    )

@inventario_bp.route('/nuevo', methods=['GET', 'POST'])
@login_required
@requiere_permiso('inventario')
def nuevo():
    if request.method == 'POST':
        insumo = Insumo(
            nombre       = request.form['nombre'],
            categoria    = request.form['categoria'],
            unidad       = request.form['unidad'],
            stock_actual = float(request.form.get('stock_actual', 0)),
            stock_minimo = float(request.form.get('stock_minimo', 0)),
            stock_maximo = float(request.form.get('stock_maximo', 0)),
            proveedor    = request.form.get('proveedor', ''),
            ubicacion    = request.form.get('ubicacion', ''),
        )
        db.session.add(insumo)
        db.session.commit()
        flash(f'Insumo "{insumo.nombre}" registrado correctamente.', 'success')
        return redirect(url_for('inventario.index'))

    return render_template('inventario/form.html', insumo=None,
                           categorias=CATEGORIAS, unidades=UNIDADES)

@inventario_bp.route('/editar/<int:id>', methods=['GET', 'POST'])
@login_required
@requiere_permiso('inventario')
def editar(id):
    insumo = Insumo.query.get_or_404(id)
    if request.method == 'POST':
        insumo.nombre       = request.form['nombre']
        insumo.categoria    = request.form['categoria']
        insumo.unidad       = request.form['unidad']
        insumo.stock_minimo = float(request.form.get('stock_minimo', 0))
        insumo.stock_maximo = float(request.form.get('stock_maximo', 0))
        insumo.proveedor    = request.form.get('proveedor', '')
        insumo.ubicacion    = request.form.get('ubicacion', '')
        db.session.commit()
        flash('Insumo actualizado.', 'success')
        return redirect(url_for('inventario.index'))

    return render_template('inventario/form.html', insumo=insumo,
                           categorias=CATEGORIAS, unidades=UNIDADES)

@inventario_bp.route('/movimiento/<int:id>', methods=['GET', 'POST'])
@login_required
@requiere_permiso('inventario')
def movimiento(id):
    insumo = Insumo.query.get_or_404(id)
    if request.method == 'POST':
        tipo     = request.form['tipo']
        cantidad = float(request.form['cantidad'])
        motivo   = request.form.get('motivo', '')

        stock_antes = insumo.stock_actual
        if tipo == 'entrada':
            insumo.stock_actual += cantidad
        elif tipo == 'salida':
            if cantidad > insumo.stock_actual:
                flash('Stock insuficiente para esta salida.', 'danger')
                return render_template('inventario/movimiento.html', insumo=insumo)
            insumo.stock_actual -= cantidad
        elif tipo == 'ajuste':
            insumo.stock_actual = cantidad

        mov = MovimientoInventario(
            insumo_id    = insumo.id,
            usuario_id   = current_user.id,
            tipo         = tipo,
            cantidad     = cantidad,
            stock_antes  = stock_antes,
            stock_despues = insumo.stock_actual,
            motivo       = motivo,
        )
        db.session.add(mov)
        db.session.commit()
        flash(f'Movimiento de {tipo} registrado. Stock actual: {insumo.stock_actual} {insumo.unidad}', 'success')
        return redirect(url_for('inventario.index'))

    return render_template('inventario/movimiento.html', insumo=insumo)

@inventario_bp.route('/historial/<int:id>')
@login_required
@requiere_permiso('inventario')
def historial(id):
    insumo = Insumo.query.get_or_404(id)
    return render_template('inventario/historial.html', insumo=insumo)

@inventario_bp.route('/eliminar/<int:id>', methods=['POST'])
@login_required
@requiere_permiso('inventario')
def eliminar(id):
    insumo = Insumo.query.get_or_404(id)
    insumo.activo = False
    db.session.commit()
    flash(f'Insumo "{insumo.nombre}" desactivado.', 'warning')
    return redirect(url_for('inventario.index'))
