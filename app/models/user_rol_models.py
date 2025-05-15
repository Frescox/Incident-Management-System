from .core import db, BaseModel
from app.utils.aes_encryption import encrypt, decrypt
import datetime
import random
import time

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
    otp_expira = db.Column(db.Integer, nullable=True)  # Changed to Integer to store Unix timestamp
    verificado = db.Column(db.Boolean, default=False)
    ultimo_login = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    # Relaciones
    rol = db.relationship('Rol', backref='usuarios')
    categorias_asignadas = db.relationship('CategoriaAgente', backref='agente', cascade='all, delete-orphan')
    
    def get_full_name(self):
        return f"{self.get_nombre_desencriptado()} {self.get_apellido_desencriptado()}"

    def save(self):
        """
        Método para guardar o actualizar el usuario en la base de datos.
        En SQLAlchemy, este método no es estrictamente necesario, pero se mantiene
        para compatibilidad con el código anterior.
        """
        if not self.id:
            db.session.add(self)
        db.session.commit()
        return self.id

    @classmethod
    def find_by_email(cls, email):
        """
        Busca un usuario por su email desencriptado.
        """
        # Esta implementación es ineficiente pero es necesaria para la búsqueda en campos encriptados
        usuarios = cls.query.filter(cls.estado == True).all()
        for usuario in usuarios:
            try:
                decrypted_email = decrypt(usuario.email) if usuario.email else ""
                if decrypted_email == email:
                    return usuario
            except Exception as e:
                print(f"[ERROR] Falló la desencriptación de email: {e}")
                continue
        return None

    @classmethod
    def find_by_id(cls, user_id):
        """
        Busca un usuario por su ID.
        """
        return cls.query.get(user_id)

    @classmethod
    def get_all_users(cls):
        """
        Obtiene todos los usuarios con información básica y roles.
        """
        usuarios_db = cls.query.join(Rol).all()
        usuarios = []
        
        for usuario in usuarios_db:
            try:
                usuario_dict = {
                    'id': usuario.id,
                    'nombre': decrypt(usuario.nombre) if usuario.nombre else "",
                    'apellido': decrypt(usuario.apellido) if usuario.apellido else "",
                    'email': decrypt(usuario.email) if usuario.email else "",
                    'estado': usuario.estado,
                    'rol_nombre': usuario.rol.nombre,
                    'rol_id': usuario.rol_id
                }
                usuarios.append(usuario_dict)
            except Exception as e:
                print(f"Error decrypting user data: {e}")
                continue
        
        return usuarios

    def verify_password(self, password):
        """
        Verifica la contraseña del usuario.
        """
        if not self.password:
            return False
        try:
            password_desencriptado = decrypt(self.password)
            return password == password_desencriptado
        except Exception as e:
            print(f"[ERROR] Falló la desencriptación de contraseña: {e}")
            return False

    def get_nombre_desencriptado(self):
        """
        Obtiene el nombre desencriptado del usuario.
        """
        return decrypt(self.nombre) if self.nombre else ""
    
    def get_apellido_desencriptado(self):
        """
        Obtiene el apellido desencriptado del usuario.
        """
        return decrypt(self.apellido) if self.apellido else ""
    
    def get_telefono_desencriptado(self):
        """
        Obtiene el teléfono desencriptado del usuario.
        """
        return decrypt(self.telefono) if self.telefono else None
    
    def generate_otp(self):
        """
        Genera un código OTP y establece su tiempo de expiración.
        """
        self.otp = str(int(random.random() * 1000000)).zfill(6)
        self.otp_expira = int(time.time()) + 900  # 15 minutos de validez
        self.save()
        return self.otp
    
    def verify_otp(self, otp):
        """
        Verifica si el OTP proporcionado es válido y no ha expirado.
        """
        current_time = int(time.time())
        if not self.otp or not self.otp_expira:
            return False
        if self.otp == otp and current_time <= self.otp_expira:
            self.verificado = True
            self.otp = None
            self.otp_expira = None
            self.save()
            return True
        return False
    
    def update_login_timestamp(self):
        """
        Actualiza la marca de tiempo del último inicio de sesión.
        """
        self.ultimo_login = datetime.datetime.utcnow()
        db.session.commit()