from models.database import db
from datetime import datetime, date

class Equipo(db.Model):
    __tablename__ = 'equipos'

    id                  = db.Column(db.Integer, primary_key=True)
    nombre              = db.Column(db.String(150), nullable=False)
    tipo                = db.Column(db.String(60), nullable=False)  # autoclave, termoselladora, etc.
    marca               = db.Column(db.String(80))
    modelo              = db.Column(db.String(80))
    numero_serie        = db.Column(db.String(80), unique=True)
    ubicacion           = db.Column(db.String(80))
    estado              = db.Column(db.String(30), default='operativo')  # operativo, mantenimiento, fuera_servicio
    fecha_adquisicion   = db.Column(db.Date)
    fecha_ultima_calibracion = db.Column(db.Date)
    fecha_proxima_calibracion = db.Column(db.Date)
    observaciones       = db.Column(db.Text)
    activo              = db.Column(db.Boolean, default=True)
    creado_en           = db.Column(db.DateTime, default=datetime.utcnow)

    mantenimientos = db.relationship('Mantenimiento', backref='equipo', lazy=True,
                                     order_by='Mantenimiento.fecha.desc()')
    ciclos         = db.relationship('Ciclo', backref='equipo', lazy=True)

    @property
    def estado_badge(self):
        badges = {
            'operativo':       ('success', 'Operativo'),
            'mantenimiento':   ('warning', 'En mantenimiento'),
            'fuera_servicio':  ('danger',  'Fuera de servicio'),
        }
        return badges.get(self.estado, ('secondary', self.estado))

    @property
    def calibracion_vigente(self):
        if not self.fecha_proxima_calibracion:
            return None
        return self.fecha_proxima_calibracion >= date.today()

    @property
    def dias_para_calibracion(self):
        if not self.fecha_proxima_calibracion:
            return None
        delta = self.fecha_proxima_calibracion - date.today()
        return delta.days

    def __repr__(self):
        return f'<Equipo {self.nombre}>'


class Mantenimiento(db.Model):
    __tablename__ = 'mantenimientos'

    id          = db.Column(db.Integer, primary_key=True)
    equipo_id   = db.Column(db.Integer, db.ForeignKey('equipos.id'), nullable=False)
    tipo        = db.Column(db.String(30), nullable=False)  # preventivo, correctivo, calibracion
    descripcion = db.Column(db.Text, nullable=False)
    tecnico_responsable = db.Column(db.String(100))
    costo       = db.Column(db.Float)
    fecha       = db.Column(db.Date, nullable=False)
    proximo_mantenimiento = db.Column(db.Date)
    creado_en   = db.Column(db.DateTime, default=datetime.utcnow)

    @property
    def tipo_display(self):
        tipos = {
            'preventivo':  'Preventivo',
            'correctivo':  'Correctivo',
            'calibracion': 'Calibración',
        }
        return tipos.get(self.tipo, self.tipo)

    @property
    def tipo_badge(self):
        return {'preventivo': 'info', 'correctivo': 'danger', 'calibracion': 'primary'}.get(self.tipo, 'secondary')
