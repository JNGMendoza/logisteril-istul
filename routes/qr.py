from flask import Blueprint, render_template, redirect, url_for, request, jsonify, abort, make_response
from flask_login import login_required, current_user
from models.database import db
from models.usuario import Usuario
from models.insumo import Insumo
from models.adquisicion import Adquisicion, AREAS_PRACTICA
from models.insumo import MovimientoInventario
from utils.qr_utils import generar_qr_base64
import hmac, hashlib, os

qr_bp = Blueprint('qr', __name__, url_prefix='/qr')

# ──────────────────────────────────────────────
# FIRMA SEGURA para tokens de QR
# ──────────────────────────────────────────────

def _firma(payload: str) -> str:
    secret = os.environ.get('SECRET_KEY', 'logisteril-istul-2024-secretkey')
    return hmac.new(secret.encode(), payload.encode(), hashlib.sha256).hexdigest()[:16]

def _token_estudiante(usuario_id: int) -> str:
    payload = f"est:{usuario_id}"
    return f"{payload}:{_firma(payload)}"

def _token_admin_stock() -> str:
    payload = "stock:admin"
    return f"{payload}:{_firma(payload)}"

def _verificar_token(token: str) -> str | None:
    """Devuelve el payload si el token es válido, None si no."""
    parts = token.rsplit(':', 1)
    if len(parts) != 2:
        return None
    payload, firma = parts
    if hmac.compare_digest(_firma(payload), firma):
        return payload
    return None


# ──────────────────────────────────────────────
# GENERAR QR ESTUDIANTE
# ──────────────────────────────────────────────

@qr_bp.route('/estudiante/<int:usuario_id>')
@login_required
def qr_estudiante(usuario_id):
    """Solo admin puede ver el QR de cualquier estudiante.
       El propio estudiante puede ver el suyo."""
    if current_user.id != usuario_id and current_user.rol not in ('admin', 'supervisor'):
        abort(403)

    usuario = Usuario.query.get_or_404(usuario_id)
    if not usuario.es_estudiante:
        abort(404)

    token = _token_estudiante(usuario_id)
    url_scan = url_for('qr.scan_estudiante', token=token, _external=True)
    qr_b64   = generar_qr_base64(url_scan, size=8)

    return render_template('qr/qr_estudiante.html',
        usuario=usuario, qr_b64=qr_b64, url_scan=url_scan)


@qr_bp.route('/todos-estudiantes')
@login_required
def todos_qr_estudiantes():
    """Admin: página con los QR de TODOS los estudiantes para imprimir."""
    if current_user.rol not in ('admin', 'supervisor', 'tecnico'):
        abort(403)

    estudiantes = Usuario.query.filter_by(rol='estudiante', activo=True)\
                               .order_by(Usuario.apellido).all()
    qrs = []
    for est in estudiantes:
        token    = _token_estudiante(est.id)
        url_scan = url_for('qr.scan_estudiante', token=token, _external=True)
        qr_b64   = generar_qr_base64(url_scan, size=5)
        qrs.append({'usuario': est, 'qr_b64': qr_b64, 'url': url_scan})

    return render_template('qr/todos_qr.html', qrs=qrs)


# ──────────────────────────────────────────────
# GENERAR QR STOCK (para admin)
# ──────────────────────────────────────────────

@qr_bp.route('/stock')
@login_required
def qr_stock():
    """Genera el QR que da acceso rápido al stock — para admin/supervisor."""
    if current_user.rol not in ('admin', 'supervisor', 'tecnico'):
        abort(403)

    token    = _token_admin_stock()
    url_scan = url_for('qr.scan_stock', token=token, _external=True)
    qr_b64   = generar_qr_base64(url_scan, size=8)

    return render_template('qr/qr_stock.html',
        qr_b64=qr_b64, url_scan=url_scan)


# ──────────────────────────────────────────────
# SCAN QR ESTUDIANTE → formulario de retiro
# ──────────────────────────────────────────────

@qr_bp.route('/retiro/<token>', methods=['GET', 'POST'])
def scan_estudiante(token):
    """
    Página pública que abre el formulario de retiro de insumos.
    Accesible sin login (el token identifica al estudiante).
    """
    payload = _verificar_token(token)
    if not payload or not payload.startswith('est:'):
        return render_template('qr/qr_invalido.html'), 403

    usuario_id = int(payload.split(':')[1])
    estudiante = Usuario.query.get_or_404(usuario_id)

    if not estudiante.activo or not estudiante.es_estudiante:
        return render_template('qr/qr_invalido.html'), 403

    insumos = Insumo.query.filter_by(activo=True)\
                          .filter(Insumo.stock_actual > 0)\
                          .order_by(Insumo.nombre).all()

    if request.method == 'POST':
        insumo_id = int(request.form['insumo_id'])
        cantidad  = float(request.form['cantidad'])
        insumo    = Insumo.query.get_or_404(insumo_id)

        if cantidad > insumo.stock_actual:
            error = f'Stock insuficiente. Disponible: {insumo.stock_actual} {insumo.unidad}'
            return render_template('qr/formulario_retiro.html',
                                   estudiante=estudiante, insumos=insumos,
                                   areas=AREAS_PRACTICA, token=token, error=error)

        # Buscar técnico de guardia (el primero activo con rol técnico)
        tecnico = Usuario.query.filter_by(rol='tecnico', activo=True).first()
        if not tecnico:
            tecnico = Usuario.query.filter_by(rol='admin', activo=True).first()

        stock_antes = insumo.stock_actual
        insumo.stock_actual -= cantidad

        adq = Adquisicion(
            estudiante_id = estudiante.id,
            area_practica = request.form['area_practica'],
            insumo_id     = insumo_id,
            cantidad      = cantidad,
            motivo        = request.form['motivo'],
            tecnico_id    = tecnico.id,
            observaciones = 'Registro vía código QR',
        )
        mov = MovimientoInventario(
            insumo_id     = insumo_id,
            usuario_id    = tecnico.id,
            tipo          = 'salida',
            cantidad      = cantidad,
            stock_antes   = stock_antes,
            stock_despues = insumo.stock_actual,
            motivo        = f'QR — {estudiante.nombre_completo} — {adq.motivo}',
        )
        db.session.add(adq)
        db.session.add(mov)
        db.session.commit()

        return render_template('qr/retiro_exitoso.html',
                               estudiante=estudiante, adq=adq, insumo=insumo)

    return render_template('qr/formulario_retiro.html',
                           estudiante=estudiante, insumos=insumos,
                           areas=AREAS_PRACTICA, token=token, error=None)


# ──────────────────────────────────────────────
# SCAN QR STOCK → vista rápida de stock
# ──────────────────────────────────────────────

@qr_bp.route('/ver-stock/<token>')
def scan_stock(token):
    """Vista pública de stock — acceso por QR seguro."""
    payload = _verificar_token(token)
    if not payload or payload != 'stock:admin':
        return render_template('qr/qr_invalido.html'), 403

    insumos = Insumo.query.filter_by(activo=True).order_by(Insumo.nombre).all()
    criticos = [i for i in insumos if i.estado_stock in ('critico', 'sin_stock')]

    return render_template('qr/stock_rapido.html',
                           insumos=insumos, criticos=criticos)
