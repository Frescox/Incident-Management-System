import pytest
from unittest.mock import patch, MagicMock
from app.utils.aes_encryption import encrypt, decrypt
from app.utils.logger import log_action
from datetime import datetime
import base64

class TestAESEncryption:
    """Pruebas para las utilidades de encriptación AES."""
    
    def test_encrypt_decrypt(self):
        """Prueba la encriptación y desencriptación de texto."""
        # Texto de prueba
        texto_original = "Texto de prueba para encriptar"
        
        # Encriptar el texto
        texto_encriptado = encrypt(texto_original)
        
        # Verificar que el texto encriptado sea diferente al original
        assert texto_encriptado != texto_original
        
        # Verificar que el texto encriptado sea una cadena base64 válida
        try:
            base64.b64decode(texto_encriptado)
        except:
            pytest.fail("El texto encriptado no es una cadena base64 válida")
        
        # Desencriptar el texto
        texto_desencriptado = decrypt(texto_encriptado)
        
        # Verificar que el texto desencriptado sea igual al original
        assert texto_desencriptado == texto_original
    
    def test_encrypt_different_results(self):
        """Prueba que la encriptación produce resultados diferentes cada vez."""
        texto = "Mismo texto para encriptar"
        
        # Encriptar el mismo texto varias veces
        encriptado1 = encrypt(texto)
        encriptado2 = encrypt(texto)
        encriptado3 = encrypt(texto)
        
        # Verificar que los resultados sean diferentes
        assert encriptado1 != encriptado2
        assert encriptado1 != encriptado3
        assert encriptado2 != encriptado3
        
        # Verificar que todos se desencriptan correctamente
        assert decrypt(encriptado1) == texto
        assert decrypt(encriptado2) == texto
        assert decrypt(encriptado3) == texto
    
    def test_decrypt_invalid_input(self):
        """Prueba la desencriptación con entrada inválida."""
        # Texto inválido (no es base64)
        texto_invalido = "Esto no es base64 válido"
        
        # Debe devolver None
        assert decrypt(texto_invalido) is None
        
        # Texto base64 válido pero no es un texto encriptado
        texto_invalido2 = base64.b64encode(b"Esto es base64 pero no encriptado").decode('utf-8')
        
        # Debe devolver None o lanzar una excepción
        try:
            result = decrypt(texto_invalido2)
            assert result is None
        except:
            # Si lanza una excepción, también es un comportamiento aceptable
            pass
    
    def test_empty_string(self):
        """Prueba la encriptación y desencriptación de cadena vacía."""
        texto_vacio = ""
        
        # Encriptar cadena vacía
        encriptado = encrypt(texto_vacio)
        
        # Verificar que produce un resultado y se puede desencriptar
        assert encriptado is not None
        assert decrypt(encriptado) == texto_vacio

class TestLogger:
    """Pruebas para el módulo de registro de actividad."""
    
    @patch('app.utils.logger.db.session')
    def test_log_action(self, mock_db_session, app):
        """Prueba el registro de una acción."""
        with app.app_context():
            # Datos de prueba
            usuario_id = 1
            accion = "crear"
            entidad = "incidencia"
            entidad_id = 123
            detalles = "Creación de incidencia de prueba"
            user_agent = "Mozilla/5.0 (Test User Agent)"
            
            # Ejecutar la función a probar
            log_action(usuario_id, accion, entidad, entidad_id, detalles, user_agent)
            
            # Verificar que se haya llamado a execute y commit
            mock_db_session.execute.assert_called_once()
            mock_db_session.commit.assert_called_once()
            
            # Obtener los parámetros con los que se llamó a execute
            args, kwargs = mock_db_session.execute.call_args
            
            # Verificar que el primer argumento sea una sentencia SQL
            assert 'INSERT INTO log_actividad' in str(args[0])
            
            # Verificar que los parámetros sean correctos
            params = kwargs.get('parameters', {})
            assert params['usuario_id'] == usuario_id
            assert params['accion'] == accion
            assert params['entidad'] == entidad
            assert params['entidad_id'] == entidad_id
            assert params['detalles'] == detalles
            assert params['user_agent'] == user_agent
    
    @patch('app.utils.logger.db.session')
    def test_log_action_error_handling(self, mock_db_session, app):
        """Prueba el manejo de errores en el registro de actividad."""
        with app.app_context():
            # Simular un error en la base de datos
            mock_db_session.execute.side_effect = Exception("Error de base de datos")
            
            # Ejecutar la función a probar
            log_action(1, "accion", "entidad", 1, "detalles")
            
            # Verificar que se haya llamado a rollback
            mock_db_session.rollback.assert_called_once()
    
    @patch('app.utils.logger.db.session')
    def test_log_action_minimal_params(self, mock_db_session, app):
        """Prueba el registro de una acción con parámetros mínimos."""
        with app.app_context():
            # Datos de prueba mínimos
            usuario_id = 1
            accion = "ver"
            entidad = "incidencia"
            entidad_id = 123
            
            # Ejecutar la función a probar con parámetros mínimos
            log_action(usuario_id, accion, entidad, entidad_id)
            
            # Verificar que se haya llamado a execute y commit
            mock_db_session.execute.assert_called_once()
            mock_db_session.commit.assert_called_once()
            
            # Obtener los parámetros con los que se llamó a execute
            args, kwargs = mock_db_session.execute.call_args
            
            # Verificar que los parámetros obligatorios estén presentes
            params = kwargs.get('parameters', {})
            assert params['usuario_id'] == usuario_id
            assert params['accion'] == accion
            assert params['entidad'] == entidad
            assert params['entidad_id'] == entidad_id
            
            # Los parámetros opcionales pueden ser None
            assert params['detalles'] is None
            assert params['user_agent'] is None