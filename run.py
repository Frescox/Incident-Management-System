from flask import Flask
from app.controllers.auth_controller import AuthController
from app.routers.routes import init_routes
from config import config
from app.services.mail_service import init_mail 
from app.models.core import db  

def create_app():
    # Inicializa la aplicación Flask
    app = Flask(__name__, template_folder='app/templates', static_folder='app/static')
    
    # Cargar configuración
    app.config.from_object(config['default'])
    
    # Inicializa Flask-Mail
    init_mail(app)  # Inicializa Flask-Mail aquí
    
    # Inicializa SQLAlchemy
    db.init_app(app)
    
    with app.app_context():
        # Importa y registra blueprints aquí
        from app.routers.routes import init_routes
        init_routes(app)
        
        # Crea tablas si no existen (solo en desarrollo)
        if app.config.get('DEBUG'):
            db.create_all()
    
    return app

if __name__ == "__main__":
    app = create_app()
    app.run(
        host=app.config.get('APP_HOST', '0.0.0.0'),
        port=app.config.get('APP_PORT', 8080),
        debug=app.config.get('DEBUG', False)
    )