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
    
    # Relación con usuarios se define en la clase Usuario

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
    
    # Métodos para añadir a la clase Usuario en app/models/user_models.py

    @classmethod
    def find_by_email(cls, email):
        """
        Busca un usuario por su email desencriptando los emails almacenados
        """
        # Buscar todos los usuarios activos
        usuarios = cls.query.filter_by(estado=True).all()
        
        # Iterar y comparar el email desencriptado
        for usuario in usuarios:
            try:
                email_desencriptado = decrypt(usuario.email)
                if email_desencriptado == email:
                    return usuario
            except Exception as e:
                print(f"[ERROR] Falló la desencriptación de email: {e}")
                continue
        
        return None

    def get_nombre_desencriptado(self):
        """Retorna el nombre desencriptado del usuario."""
        return decrypt(self.nombre) if self.nombre else ""

    def get_apellido_desencriptado(self):
        """Retorna el apellido desencriptado del usuario."""
        return decrypt(self.apellido) if self.apellido else ""

    def get_email_desencriptado(self):
        """Retorna el email desencriptado del usuario."""
        return decrypt(self.email) if self.email else ""

    def get_telefono_desencriptado(self):
        """Retorna el teléfono desencriptado del usuario."""
        return decrypt(self.telefono) if self.telefono else None

    def verify_password(self, password):
        """Verifica si la contraseña dada coincide con la del usuario."""
        if not self.password:
            return False
        try:
            password_desencriptado = decrypt(self.password)
            return password == password_desencriptado
        except Exception as e:
            print(f"[ERROR] Falló la desencriptación de contraseña: {e}")
            return False

    # En el método generate_otp
    def generate_otp(self):
        otp = str(random.randint(100000, 999999))
        self.otp = otp
        # Guardar como timestamp (entero)
        self.otp_expira = int((datetime.datetime.now() + datetime.timedelta(minutes=15)).timestamp())
        db.session.commit()
        return otp

    # En el método verify_otp
    def verify_otp(self, otp):
        if not self.otp or not self.otp_expira:
            return False
        
        current_time = int(datetime.datetime.now().timestamp())
        
        if self.otp == otp and current_time <= self.otp_expira:
            self.verificado = True
            self.otp = None
            self.otp_expira = None
            db.session.commit()
            return True
        return False

    def update_login_timestamp(self):
        """Actualiza la marca de tiempo del último inicio de sesión."""
        self.ultimo_login = datetime.datetime.now()
        db.session.commit()

    @classmethod
    def get_all_users(cls):
        """Retorna todos los usuarios con sus datos desencriptados."""
        users = cls.query.all()
        usuarios = []
        
        for user in users:
            try:
                usuario = {
                    'id': user.id,
                    'nombre': decrypt(user.nombre) if user.nombre else "",
                    'apellido': decrypt(user.apellido) if user.apellido else "",
                    'email': decrypt(user.email) if user.email else "",
                    'estado': user.estado,
                    'rol_nombre': user.rol.nombre if user.rol else "",
                    'rol_id': user.rol_id
                }
                usuarios.append(usuario)
            except Exception as e:
                print(f"Error desencriptando datos de usuario: {e}")
                continue
        
        return usuarios