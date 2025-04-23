from .core import db, BaseModel
from app.utils.aes_encryption import encrypt, decrypt
import datetime
import random
from .catalog_models import CategoriaAgente

class Rol(BaseModel):
    __tablename__ = 'roles'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), unique=True, nullable=False)
    descripcion = db.Column(db.Text)
    
class Usuario(BaseModel):
    __tablename__ = 'usuarios'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    apellido = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    rol_id = db.Column(db.Integer, db.ForeignKey('roles.id'), nullable=False)
    estado = db.Column(db.Boolean, default=True)
    telefono = db.Column(db.String(20), nullable=True)
    metodo_verificacion = db.Column(db.String(10), nullable=True)
    otp = db.Column(db.String(6), nullable=True)
    otp_expira = db.Column(db.DateTime, nullable=True)
    verificado = db.Column(db.Boolean, default=False)
    ultimo_login = db.Column(db.DateTime, nullable=True)

    # Relaciones
    rol = db.relationship('Rol', backref='usuarios')
    categorias_asignadas = db.relationship('CategoriaAgente', backref='agente', cascade='all, delete-orphan')
    
    def get_full_name(self):
        return f"{self.nombre} {self.apellido}"

    @classmethod
    def find_by_email(cls, email):
        return cls.query.filter_by(email=email).first()