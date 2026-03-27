from flask import Blueprint, render_template, redirect, url_for, request, jsonify, abort
from flask_login import login_required, current_user
from models.database import db
from models.usuario import Usuario
from models.insumo import Insumo
from models.adquisicion import Adquisicion, AREAS_PRACTICA
from models.insumo import MovimientoInventario
from utils.qr_utils import generar_qr_base64
import hmac, hashlib, os

qr_bp = Blueprint('qr', __name__, url_prefix='/qr')

# ── Token seguro para el QR de stock ──────────────────────────────────────────
def _firma(payload: str) -> str:
    secret = os.environ.get('SECRET_KEY', 'logisteril-istul-2024-secretkey')
    return hmac.new(secret.encode(), payload.encode(), hashlib.sha256).hexdigest()[:16]

def _token_stock() -> str:
    payload = "stock:admin"
    return f"{payload}:{_firma(payload)}"

def _verificar_token_stock(token: str) -> bool:
    parts = token.rsplit(':', 1)
    if len(parts) != 2:
        return False
    payload, firma = parts
    return hmac.compare_digest(_firma(payload), firma) and payload == "stock:admin"


# ── QR ÚNICO DE RETIRO (para imprimir y pegar en la central) ──────────────────

@qr_bp.route('/retiro')
@login_required
def qr_retiro():
    """Admin/técnico genera el QR único del sistema para retiro de insumos."""
    if current_user.rol not in ('admin', 'supervisor', 'tecnico'):
        abort(403)
    url_scan = url_for('qr.scan_retiro', _external=True)
    qr_b64   = generar_qr_base64(url_scan, size=10)
    return render_template('qr/qr_retiro_unico.html', qr_b64=qr_b64, url_scan=url_scan)


# ── PASO 1 — El estudiante escanea: ingresa su cédula ─────────────────────────

@qr_bp.route('/retiro/inicio', methods=['GET', 'POST'])
def scan_retiro():
    """Página pública. El estudiante ingresa su cédula para identificarse."""
    error = None

    if request.method == 'POST':
        cedula = request.form.get('cedula', '').strip()

        if not cedula:
            error = 'Ingresa tu número de cédula.'
        else:
            # Buscar por cédula o código de estudiante
            estudiante = Usuario.query.filter(
                Usuario.rol == 'estudiante',
                Usuario.activo == True,
                (Usuario.cedula == cedula) | (Usuario.codigo_estudiante == cedula)
            ).first()

            if not estudiante:
                error = f'No se encontró ningún estudiante con la cédula o código "{cedula}". Verifica el número o contacta al técnico.'
            else:
                # Redirigir al formulario con el ID del estudiante en sesión de URL
                return redirect(url_for('qr.formulario_retiro', estudiante_id=estudiante.id))

    return render_template('qr/cedula_inicio.html', error=error)


# ── PASO 2 — Formulario de retiro identificado ────────────────────────────────

@qr_bp.route('/retiro/formulario/<int:estudiante_id>', methods=['GET', 'POST'])
def formulario_retiro(estudiante_id):
    """Formulario de retiro ya identificado con el estudiante."""
    estudiante = Usuario.query.filter_by(
        id=estudiante_id, rol='estudiante', activo=True
    ).first_or_404()

    insumos = Insumo.query.filter_by(activo=True)\
                          .filter(Insumo.stock_actual > 0)\
                          .order_by(Insumo.nombre).all()
    error = None

    if request.method == 'POST':
        insumo_id = request.form.get('insumo_id', '')
        cantidad_str = request.form.get('cantidad', '')
        area = request.form.get('area_practica', '')
        motivo = request.form.get('motivo', '').strip()

        # Validaciones
        if not insumo_id or not cantidad_str or not area or not motivo:
            error = 'Todos los campos son obligatorios.'
        else:
            cantidad = float(cantidad_str)
            insumo   = Insumo.query.get_or_404(int(insumo_id))

            if cantidad <= 0:
                error = 'La cantidad debe ser mayor a cero.'
            elif cantidad > insumo.stock_actual:
                error = f'Stock insuficiente. Disponible: {insumo.stock_actual} {insumo.unidad}'

        if not error:
            # Buscar técnico activo para asignar la entrega
            tecnico = Usuario.query.filter(
                Usuario.rol.in_(['tecnico', 'admin']),
                Usuario.activo == True
            ).first()

            stock_antes = insumo.stock_actual
            insumo.stock_actual -= cantidad

            adq = Adquisicion(
                estudiante_id = estudiante.id,
                area_practica = area,
                insumo_id     = int(insumo_id),
                cantidad      = cantidad,
                motivo        = motivo,
                tecnico_id    = tecnico.id,
                observaciones = 'Registro vía código QR del sistema',
            )
            mov = MovimientoInventario(
                insumo_id     = int(insumo_id),
                usuario_id    = tecnico.id,
                tipo          = 'salida',
                cantidad      = cantidad,
                stock_antes   = stock_antes,
                stock_despues = insumo.stock_actual,
                motivo        = f'QR — {estudiante.nombre_completo} — {motivo}',
            )
            db.session.add(adq)
            db.session.add(mov)
            db.session.commit()

            return render_template('qr/retiro_exitoso.html',
                                   estudiante=estudiante, adq=adq, insumo=insumo)

    return render_template('qr/formulario_retiro.html',
                           estudiante=estudiante, insumos=insumos,
                           areas=AREAS_PRACTICA, error=error)


# ── QR STOCK (para admin/supervisor) ─────────────────────────────────────────

@qr_bp.route('/stock')
@login_required
def qr_stock():
    if current_user.rol not in ('admin', 'supervisor', 'tecnico'):
        abort(403)
    token    = _token_stock()
    url_scan = url_for('qr.scan_stock', token=token, _external=True)
    qr_b64   = generar_qr_base64(url_scan, size=8)
    return render_template('qr/qr_stock.html', qr_b64=qr_b64, url_scan=url_scan)


@qr_bp.route('/ver-stock/<token>')
def scan_stock(token):
    if not _verificar_token_stock(token):
        return render_template('qr/qr_invalido.html'), 403
    from datetime import datetime
    insumos  = Insumo.query.filter_by(activo=True).order_by(Insumo.nombre).all()
    criticos = [i for i in insumos if i.estado_stock in ('critico', 'sin_stock')]
    return render_template('qr/stock_rapido.html',
                           insumos=insumos, criticos=criticos,
                           now=datetime.now())
