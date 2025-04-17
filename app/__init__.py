from flask import Flask
from config import config

def create_app(config_name='default'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Inicializar extensiones
    from app.models.core import db
    db.init_app(app)
    
    # Registrar blueprints
    from app.routers.routes import init_routes
    init_routes(app)
    
    # Crear tablas en desarrollo
    with app.app_context():
        if app.config['DEBUG']:
            db.create_all()
    
    return app