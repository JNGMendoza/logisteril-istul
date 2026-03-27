from models.database import db
from datetime import datetime

AREAS_PRACTICA = [
    'Laboratorio de esterilización',
    'Quirófano de prácticas',
    'Sala de procedimientos',
    'Laboratorio clínico',
    'Área de enfermería',
    'Sala de simulación',
    'Otro',
]

class Adquisicion(db.Model):
    __tablename__ = 'adquisiciones'

    id              = db.Column(db.Integer, primary_key=True)
    # Quién retira
    estudiante_id   = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=True)
    # Datos manuales si no tiene cuenta (retiro presencial)
    solicitante_nombre   = db.Column(db.String(150))
    solicitante_cedula   = db.Column(db.String(20))
    solicitante_codigo   = db.Column(db.String(20))
    solicitante_carrera  = db.Column(db.String(100))
    solicitante_semestre = db.Column(db.String(20))
    area_practica        = db.Column(db.String(100), nullable=False)
    # Qué insumo
    insumo_id       = db.Column(db.Integer, db.ForeignKey('insumos.id'), nullable=False)
    cantidad        = db.Column(db.Float, nullable=False)
    motivo          = db.Column(db.String(300), nullable=False)
    # Quién entregó (técnico)
    tecnico_id      = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    # Auditoría
    fecha           = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    observaciones   = db.Column(db.Text)

    # Relación al insumo
    insumo = db.relationship('Insumo', backref='adquisiciones', lazy=True)

    @property
    def nombre_solicitante(self):
        """Devuelve el nombre del solicitante sea por cuenta o manual."""
        if self.estudiante:
            return self.estudiante.nombre_completo
        return self.solicitante_nombre or 'Sin nombre'

    @property
    def cedula_solicitante(self):
        if self.estudiante:
            return self.estudiante.cedula or self.estudiante.codigo_estudiante or '—'
        return self.solicitante_cedula or self.solicitante_codigo or '—'

    @property
    def area_solicitante(self):
        return self.area_practica

    @property
    def carrera_solicitante(self):
        if self.estudiante:
            return self.estudiante.carrera or '—'
        return self.solicitante_carrera or '—'

    def __repr__(self):
        return f'<Adquisicion {self.id} - {self.nombre_solicitante}>'
