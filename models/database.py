from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

def init_db():
    db.create_all()
    from models.usuario import Usuario
    from models.insumo import Insumo

    if not Usuario.query.filter_by(username='admin').first():
        admin = Usuario(
            username='admin', nombre='Administrador', apellido='Sistema',
            email='admin@istul.edu.ec', rol='admin', activo=True
        )
        admin.set_password('Admin1234!')
        db.session.add(admin)

        supervisor = Usuario(
            username='supervisor', nombre='Supervisora', apellido='Esterilización',
            email='supervisor@istul.edu.ec', rol='supervisor', activo=True
        )
        supervisor.set_password('Super1234!')
        db.session.add(supervisor)

        tecnico = Usuario(
            username='tecnico', nombre='Técnico', apellido='Central',
            email='tecnico@istul.edu.ec', rol='tecnico', activo=True
        )
        tecnico.set_password('Tecnico1234!')
        db.session.add(tecnico)

        # Estudiantes de ejemplo
        estudiantes_demo = [
            ('est001', 'María', 'González', 'est001@istul.edu.ec',
             '1712345678', 'EST-2024-001', 'Enfermería', '3er semestre'),
            ('est002', 'Carlos', 'Mejía', 'est002@istul.edu.ec',
             '1787654321', 'EST-2024-002', 'Instrumentación Quirúrgica', '5to semestre'),
            ('est003', 'Ana', 'Paredes', 'est003@istul.edu.ec',
             '1756789012', 'EST-2024-003', 'Enfermería', '3er semestre'),
        ]
        for u, n, a, e, ced, cod, car, sem in estudiantes_demo:
            est = Usuario(
                username=u, nombre=n, apellido=a, email=e,
                rol='estudiante', activo=True,
                cedula=ced, codigo_estudiante=cod,
                carrera=car, semestre=sem
            )
            est.set_password('Estud1234!')
            db.session.add(est)

        # Insumos de ejemplo
        insumos_ejemplo = [
            Insumo(nombre='Bolsas de esterilización 100x250mm', categoria='Empaque',
                   unidad='Unidad', stock_actual=500, stock_minimo=100, stock_maximo=1000,
                   proveedor='MedSupply Ecuador', ubicacion='Bodega A-1'),
            Insumo(nombre='Cinta indicadora clase 1', categoria='Indicadores',
                   unidad='Rollo', stock_actual=15, stock_minimo=10, stock_maximo=50,
                   proveedor='3M Ecuador', ubicacion='Bodega A-2'),
            Insumo(nombre='Detergente enzimático multienzimático', categoria='Limpieza',
                   unidad='Litro', stock_actual=8, stock_minimo=10, stock_maximo=40,
                   proveedor='CleanMed S.A.', ubicacion='Bodega B-1'),
            Insumo(nombre='Indicador biológico Geobacillus', categoria='Indicadores',
                   unidad='Ampolla', stock_actual=30, stock_minimo=20, stock_maximo=80,
                   proveedor='MedSupply Ecuador', ubicacion='Refrigerador C-1'),
            Insumo(nombre='Tela no tejida SMS 60g', categoria='Empaque',
                   unidad='Metro', stock_actual=200, stock_minimo=50, stock_maximo=400,
                   proveedor='TextilMed', ubicacion='Bodega A-3'),
            Insumo(nombre='Guantes estériles talla M', categoria='Descartable',
                   unidad='Par', stock_actual=120, stock_minimo=30, stock_maximo=200,
                   proveedor='MedSupply Ecuador', ubicacion='Bodega B-2'),
            Insumo(nombre='Gasas estériles 10x10cm', categoria='Descartable',
                   unidad='Paquete', stock_actual=80, stock_minimo=20, stock_maximo=150,
                   proveedor='CleanMed S.A.', ubicacion='Bodega B-3'),
        ]
        for insumo in insumos_ejemplo:
            db.session.add(insumo)

        db.session.commit()
        print("✅ Base de datos inicializada con datos de ejemplo.")
