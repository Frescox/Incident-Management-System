from flask import Flask
from app.db.database import db
from app.services.mail_service import init_mail
from app.routers.routes import init_routes
from config import config

def create_app(config_name='default'):
    """
    Crea y configura una instancia de la aplicación Flask
    
    Args:
        config_name (str): Nombre de la configuración a utilizar
        
    Returns:
        La aplicación Flask configurada
    """
    app = Flask(__name__)
    
    # Cargar configuración
    app.config.from_object(config[config_name])
    
    # Inicializar servicios
    init_mail(app)
    
    # Registrar rutas
    with app.app_context():
        init_routes(app)
    
    return app