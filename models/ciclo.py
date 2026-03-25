from models.database import db
from datetime import datetime

class Ciclo(db.Model):
    __tablename__ = 'ciclos'

    id                  = db.Column(db.Integer, primary_key=True)
    numero_ciclo        = db.Column(db.String(20), unique=True, nullable=False)
    equipo_id           = db.Column(db.Integer, db.ForeignKey('equipos.id'), nullable=False)
    usuario_id          = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    metodo              = db.Column(db.String(60), nullable=False)  # vapor, EO, plasma, calor_seco
    temperatura         = db.Column(db.Float)
    presion             = db.Column(db.Float)
    tiempo_minutos      = db.Column(db.Integer)
    contenido           = db.Column(db.Text, nullable=False)  # descripción del instrumental/material
    servicio_destino    = db.Column(db.String(100))
    lote                = db.Column(db.String(50))
    indicador_quimico   = db.Column(db.String(20), default='pendiente')  # aprobado, rechazado, pendiente
    indicador_biologico = db.Column(db.String(20), default='pendiente')
    resultado           = db.Column(db.String(20), default='en_proceso')  # aprobado, rechazado, en_proceso
    observaciones       = db.Column(db.Text)
    fecha_inicio        = db.Column(db.DateTime, default=datetime.utcnow)
    fecha_fin           = db.Column(db.DateTime)
    creado_en           = db.Column(db.DateTime, default=datetime.utcnow)

    @property
    def metodo_display(self):
        metodos = {
            'vapor':      'Vapor saturado (Autoclave)',
            'EO':         'Óxido de etileno',
            'plasma':     'Plasma de peróxido de hidrógeno',
            'calor_seco': 'Calor seco',
        }
        return metodos.get(self.metodo, self.metodo)

    @property
    def resultado_badge(self):
        badges = {
            'aprobado':   ('success', 'Aprobado'),
            'rechazado':  ('danger',  'Rechazado'),
            'en_proceso': ('warning', 'En proceso'),
        }
        return badges.get(self.resultado, ('secondary', self.resultado))

    @property
    def indicador_badge(self):
        badges = {
            'aprobado':  ('success', 'Aprobado'),
            'rechazado': ('danger',  'Rechazado'),
            'pendiente': ('warning', 'Pendiente'),
        }
        return badges.get(self.indicador_quimico, ('secondary', '-'))

    def __repr__(self):
        return f'<Ciclo {self.numero_ciclo}>'
