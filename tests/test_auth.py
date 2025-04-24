import pytest
from flask import session
from app.models.user_models import Usuario
from app.utils.aes_encryption import encrypt, decrypt

class TestAuthController:
    """Pruebas para el controlador de autenticación."""
    
    def test_index_page(self, client):
        """Prueba que la página de inicio se cargue correctamente."""
        response = client.get('/')
        assert response.status_code == 200
        assert b'Sistema de Gesti' in response.data  # Verifica parte del título
        assert b'Iniciar Sesi' in response.data  # Verifica que aparezca el formulario de login
    
    def test_login_success(self, client, init_database):
        """Prueba que el inicio de sesión funcione correctamente con credenciales válidas."""
        response = client.post('/login', data={
            'email': 'admin@sistema.com',
            'password': 'adminsistema'
        }, follow_redirects=True)
        
        # Debe devolver éxito y la URL de redirección
        json_data = response.get_json()
        assert json_data['success'] is True
        assert 'redirect' in json_data
        assert 'admin/dashboard' in json_data['redirect']
    
    def test_login_invalid_credentials(self, client, init_database):
        """Prueba que el inicio de sesión falle con credenciales inválidas."""
        response = client.post('/login', data={
            'email': 'admin@sistema.com',
            'password': 'contraseña_incorrecta'
        })
        
        json_data = response.get_json()
        assert json_data['success'] is False
        assert 'Credenciales inv' in json_data['message']
    
    def test_register_user(self, client, app):
        """Prueba el registro de un nuevo usuario."""
        with app.app_context():
            # Contar usuarios antes del registro
            initial_count = Usuario.query.count() if hasattr(Usuario, 'query') else 0
        
        response = client.post('/register', data={
            'nombre': 'NuevoUsuario',
            'apellido': 'Apellido',
            'email': 'nuevo@ejemplo.com',
            'password': 'clave123',
            'metodo_verificacion': 'email'
        })
        
        json_data = response.get_json()
        assert json_data['success'] is True
        assert 'show_otp_verification' in json_data
        
        # Verificar que el usuario se haya creado en la BD
        with app.app_context():
            if hasattr(Usuario, 'query'):
                assert Usuario.query.count() > initial_count
            
            # O si usamos el método personalizado de búsqueda
            user = Usuario.find_by_email('nuevo@ejemplo.com')
            assert user is not None
    
    def test_verify_otp(self, client, app, monkeypatch):
        """Prueba la verificación de OTP."""
        # Primero registramos un usuario
        client.post('/register', data={
            'nombre': 'UsuarioOTP',
            'apellido': 'Verificacion',
            'email': 'otp@ejemplo.com',
            'password': 'clave123',
            'metodo_verificacion': 'email'
        })
        
        # Establecemos el email en la sesión (simulando el registro anterior)
        with client.session_transaction() as sess:
            sess['user_email'] = 'otp@ejemplo.com'
        
        # Obtenemos el usuario y su OTP
        with app.app_context():
            user = Usuario.find_by_email('otp@ejemplo.com')
            assert user is not None
            
            # Simulamos que ya tiene un OTP generado
            test_otp = '123456'
            user.otp = test_otp
            user.otp_expira = int(pytest.importorskip("time").time()) + 300  # 5 minutos en el futuro
            
            # Guardamos el usuario con el OTP simulado
            if hasattr(user, 'save'):
                user.save()
        
        # Ahora intentamos verificar con ese OTP
        response = client.post('/verify_otp', data={'otp': test_otp})
        
        json_data = response.get_json()
        assert json_data['success'] is True
        assert 'redirect' in json_data
    
    def test_logout(self, client, init_database):
        """Prueba que el cierre de sesión funcione correctamente."""
        # Primero iniciamos sesión
        client.post('/login', data={
            'email': 'admin@sistema.com',
            'password': 'adminsistema'
        })
        
        # Luego hacemos logout
        response = client.get('/logout', follow_redirects=True)
        
        # Debería redirigir a la página de inicio
        assert response.status_code == 200
        assert b'Sistema de Gesti' in response.data
        
        # Verificar que la sesión se haya borrado
        with client.session_transaction() as sess:
            assert 'user_id' not in sess
            assert 'user_email' not in sess