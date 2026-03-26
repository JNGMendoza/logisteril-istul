from flask import Flask
from flask_login import LoginManager
from models.database import db, init_db
from models.usuario import Usuario
from routes.auth import auth_bp
from routes.dashboard import dashboard_bp
from routes.inventario import inventario_bp
from routes.equipos import equipos_bp
from routes.ciclos import ciclos_bp
from routes.reportes import reportes_bp
from routes.usuarios import usuarios_bp
from utils.context import register_context_processors
from dotenv import load_dotenv
import os

load_dotenv()

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'logisteril-istul-2024-secretkey')

    # Render entrega DATABASE_URL como "postgres://..." pero SQLAlchemy necesita "postgresql://"
    database_url = os.environ.get('DATABASE_URL', 'sqlite:///logisteril.db')
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Por favor inicia sesión para continuar.'
    login_manager.login_message_category = 'warning'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return Usuario.query.get(int(user_id))

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(inventario_bp)
    app.register_blueprint(equipos_bp)
    app.register_blueprint(ciclos_bp)
    app.register_blueprint(reportes_bp)
    app.register_blueprint(usuarios_bp)

    register_context_processors(app)

    with app.app_context():
        init_db()

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=False, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
