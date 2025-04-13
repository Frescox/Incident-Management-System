import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'clave-secreta'
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:@localhost/sistema_incidencias'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = 'static/uploads'
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5MB
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}