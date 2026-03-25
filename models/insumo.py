from models.database import db
from datetime import datetime

class Insumo(db.Model):
    __tablename__ = 'insumos'

    id            = db.Column(db.Integer, primary_key=True)
    nombre        = db.Column(db.String(150), nullable=False)
    categoria     = db.Column(db.String(60), nullable=False)
    unidad        = db.Column(db.String(30), nullable=False)
    stock_actual  = db.Column(db.Float, default=0)
    stock_minimo  = db.Column(db.Float, default=0)
    stock_maximo  = db.Column(db.Float, default=0)
    proveedor     = db.Column(db.String(100))
    ubicacion     = db.Column(db.String(80))
    activo        = db.Column(db.Boolean, default=True)
    creado_en     = db.Column(db.DateTime, default=datetime.utcnow)
    actualizado_en = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    movimientos = db.relationship('MovimientoInventario', backref='insumo', lazy=True,
                                  order_by='MovimientoInventario.fecha.desc()')

    @property
    def estado_stock(self):
        if self.stock_actual <= 0:
            return 'sin_stock'
        elif self.stock_actual <= self.stock_minimo:
            return 'critico'
        elif self.stock_actual <= self.stock_minimo * 1.5:
            return 'bajo'
        return 'normal'

    @property
    def estado_badge(self):
        badges = {
            'sin_stock': ('danger', 'Sin stock'),
            'critico':   ('danger', 'Crítico'),
            'bajo':      ('warning', 'Bajo'),
            'normal':    ('success', 'Normal'),
        }
        return badges.get(self.estado_stock, ('secondary', 'Desconocido'))

    def __repr__(self):
        return f'<Insumo {self.nombre}>'


class MovimientoInventario(db.Model):
    __tablename__ = 'movimientos_inventario'

    id          = db.Column(db.Integer, primary_key=True)
    insumo_id   = db.Column(db.Integer, db.ForeignKey('insumos.id'), nullable=False)
    usuario_id  = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    tipo        = db.Column(db.String(20), nullable=False)  # entrada, salida, ajuste
    cantidad    = db.Column(db.Float, nullable=False)
    stock_antes = db.Column(db.Float)
    stock_despues = db.Column(db.Float)
    motivo      = db.Column(db.String(200))
    fecha       = db.Column(db.DateTime, default=datetime.utcnow)

    @property
    def tipo_display(self):
        tipos = {'entrada': 'Entrada', 'salida': 'Salida', 'ajuste': 'Ajuste'}
        return tipos.get(self.tipo, self.tipo)

    @property
    def tipo_badge(self):
        badges = {
            'entrada': 'success',
            'salida':  'primary',
            'ajuste':  'warning',
        }
        return badges.get(self.tipo, 'secondary')
