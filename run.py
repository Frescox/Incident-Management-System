from flask import Flask
from app.controllers.auth_controller import AuthController
from app.routers.routes import init_routes
from app.db.database import db
from config import config
from app.services.mail_service import init_mail  # Importa la función de inicialización de mail

def create_app():
    # Inicializar la aplicación Flask
    app = Flask(__name__, template_folder='app/templates')
    
    # Cargar configuración
    app.config.from_object(config['default'])
    
    # Inicializar Flask-Mail
    init_mail(app)  # Inicializa Flask-Mail aquí
    
    # Configurar contexto de aplicación para la base de datos
    with app.app_context():
        # Inicializar rutas
        init_routes(app)
    
    return app

if __name__ == "__main__":
    app = create_app()
    app.run(
        host=app.config.get('APP_HOST', '0.0.0.0'),
        port=app.config.get('APP_PORT', 5000),
        debug=app.config.get('DEBUG', False)
    )
