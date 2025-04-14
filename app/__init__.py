from flask import Flask
from config import Config
from app.models import db  # Importa db desde models

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    db.init_app(app)
    
    with app.app_context():
        db.create_all()  # Opcional: crea tablas si no existen
    
    return app