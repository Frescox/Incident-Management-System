import pytest
import time
from app.models.user_models import Usuario
from app.utils.aes_encryption import encrypt, decrypt

class TestUsuarioModel:
    """Pruebas para el modelo Usuario."""
    
    def test_create_user(self, app, init_database):
        """Prueba la creación de un usuario."""
        with app.app_context():
            # Crear un nuevo usuario
            nuevo_usuario = Usuario(
                nombre=encrypt('Test'),
                apellido=encrypt('Usuario'),
                email=encrypt('test.usuario@ejemplo.com'),
                password=encrypt('password123'),
                rol_id=3,  # Rol usuario
                estado=True,
                verificado=False
            )
            
            # Guardar el usuario
            assert nuevo_usuario.save() is not None
            
            # Verificar que el usuario se haya guardado correctamente
            usuario_recuperado = Usuario.find_by_email('test.usuario@ejemplo.com')
            assert usuario_recuperado is not None
            
            # Verificar que los datos se hayan guardado correctamente
            assert decrypt(usuario_recuperado.nombre) == 'Test'
            assert decrypt(usuario_recuperado.apellido) == 'Usuario'
            assert decrypt(usuario_recuperado.email) == 'test.usuario@ejemplo.com'
            assert usuario_recuperado.rol_id == 3
            assert usuario_recuperado.estado is True
            assert usuario_recuperado.verificado is False
    
    def test_find_by_email(self, app, init_database):
        """Prueba la búsqueda de un usuario por email."""
        with app.app_context():
            # Buscar un usuario que sabemos que existe
            usuario = Usuario.find_by_email('admin@sistema.com')
            
            # Verificar que el usuario exista
            assert usuario is not None
            assert decrypt(usuario.email) == 'admin@sistema.com'
            
            # Buscar un usuario que no existe
            usuario_inexistente = Usuario.find_by_email('no.existe@ejemplo.com')
            assert usuario_inexistente is None
    
    def test_find_by_id(self, app, init_database):
        """Prueba la búsqueda de un usuario por ID."""
        with app.app_context():
            # Primero encontramos un usuario para obtener su ID
            admin = Usuario.find_by_email('admin@sistema.com')
            assert admin is not None
            
            # Ahora buscamos por ese ID
            usuario = Usuario.find_by_id(admin.id)
            assert usuario is not None
            assert usuario.id == admin.id
            
            # Buscar un ID que no existe
            usuario_inexistente = Usuario.find_by_id(9999)
            assert usuario_inexistente is None
    
    def test_verify_password(self, app, init_database):
        """Prueba la verificación de contraseña."""
        with app.app_context():
            # Buscar un usuario
            usuario = Usuario.find_by_email('admin@sistema.com')
            assert usuario is not None
            
            # Verificar contraseña correcta
            assert usuario.verify_password('adminsistema') is True
            
            # Verificar contraseña incorrecta
            assert usuario.verify_password('contraseña_incorrecta') is False
    
    def test_generate_and_verify_otp(self, app, init_database):
        """Prueba la generación y verificación de OTP."""
        with app.app_context():
            # Buscar un usuario
            usuario = Usuario.find_by_email('usuario@sistema.com')
            assert usuario is not None
            
            # Generar OTP
            otp = usuario.generate_otp()
            assert otp is not None
            assert len(otp) == 6
            assert usuario.otp == otp
            assert usuario.otp_expira is not None
            
            # Verificar OTP correcto
            assert usuario.verify_otp(otp) is True
            
            # Después de verificar, el OTP debe ser None y el usuario verificado
            assert usuario.otp is None
            assert usuario.otp_expira is None
            assert usuario.verificado is True
    
    def test_expired_otp(self, app, init_database):
        """Prueba que un OTP expirado no sea válido."""
        with app.app_context():
            # Buscar un usuario
            usuario = Usuario.find_by_email('agente@sistema.com')
            assert usuario is not None
            
            # Generar OTP pero establecer expiración en el pasado
            otp = usuario.generate_otp()
            usuario.otp_expira = int(time.time()) - 3600  # 1 hora en el pasado
            usuario.save()
            
            # Verificar que el OTP expirado no sea válido
            assert usuario.verify_otp(otp) is False
            
            # El usuario no debe estar verificado
            assert usuario.verificado is False
    
    def test_update_login_timestamp(self, app, init_database):
        """Prueba la actualización del tiempo de último login."""
        with app.app_context():
            usuario = Usuario.find_by_email('admin@sistema.com')
            assert usuario is not None
            
            # Guardar timestamp actual
            ultimo_login_anterior = usuario.ultimo_login
            
            # Actualizar timestamp
            usuario.update_login_timestamp()
            
            # Recargar usuario
            usuario_actualizado = Usuario.find_by_id(usuario.id)
            
            # Verificar que el timestamp se haya actualizado
            if ultimo_login_anterior is None:
                assert usuario_actualizado.ultimo_login is not None
            else:
                assert usuario_actualizado.ultimo_login != ultimo_login_anterior