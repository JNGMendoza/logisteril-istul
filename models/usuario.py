from models.database import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

ROLES = {
    'admin':      'Administrador',
    'supervisor': 'Supervisor/Jefe',
    'tecnico':    'Técnico de Esterilización',
    'estudiante': 'Estudiante',
}

PERMISOS = {
    'admin':      ['inventario', 'equipos', 'ciclos', 'reportes', 'usuarios', 'adquisiciones'],
    'supervisor': ['inventario', 'equipos', 'ciclos', 'reportes', 'adquisiciones'],
    'tecnico':    ['inventario', 'equipos', 'ciclos', 'adquisiciones'],
    'estudiante': ['mis_solicitudes'],
}

class Usuario(UserMixin, db.Model):
    __tablename__ = 'usuarios'

    id            = db.Column(db.Integer, primary_key=True)
    username      = db.Column(db.String(50), unique=True, nullable=False)
    nombre        = db.Column(db.String(80), nullable=False)
    apellido      = db.Column(db.String(80), nullable=False)
    email         = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    rol           = db.Column(db.String(20), nullable=False, default='estudiante')
    # Campos extra para estudiantes
    cedula        = db.Column(db.String(20))
    codigo_estudiante = db.Column(db.String(20))
    carrera       = db.Column(db.String(100))
    semestre      = db.Column(db.String(20))
    activo        = db.Column(db.Boolean, default=True)
    creado_en     = db.Column(db.DateTime, default=datetime.utcnow)
    ultimo_login  = db.Column(db.DateTime)

    # Relaciones
    ciclos_registrados = db.relationship('Ciclo', backref='registrado_por', lazy=True)
    movimientos        = db.relationship('MovimientoInventario', backref='usuario', lazy=True)
    adquisiciones_como_tecnico    = db.relationship(
        'Adquisicion', foreign_keys='Adquisicion.tecnico_id', backref='tecnico', lazy=True)
    adquisiciones_como_estudiante = db.relationship(
        'Adquisicion', foreign_keys='Adquisicion.estudiante_id', backref='estudiante', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def tiene_permiso(self, modulo):
        return modulo in PERMISOS.get(self.rol, [])

    @property
    def nombre_completo(self):
        return f"{self.nombre} {self.apellido}"

    @property
    def rol_display(self):
        return ROLES.get(self.rol, self.rol)

    @property
    def es_estudiante(self):
        return self.rol == 'estudiante'

    def __repr__(self):
        return f'<Usuario {self.username} [{self.rol}]>'
