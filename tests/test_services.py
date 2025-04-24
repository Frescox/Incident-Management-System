import pytest
from unittest.mock import patch, MagicMock
from app.services.assignment_service import AssignmentService
from app.services.notification_service import NotificationService
from app.services.mail_service import send_email
from app.models.user_models import Usuario
from app.models.ticket_models import Incidencia
from app.utils.aes_encryption import encrypt, decrypt

class TestAssignmentService:
    """Pruebas para el servicio de asignación de incidencias."""
    
    def test_get_available_agents(self, app, init_database):
        """Prueba la obtención de agentes disponibles."""
        with app.app_context():
            # Crear una instancia del servicio
            service = AssignmentService()
            
            # Ejecutar el método a probar
            agentes = service.get_available_agents()
            
            # Verificar que se hayan recuperado agentes
            assert isinstance(agentes, list)
            
            # Verificar que los agentes tengan los campos esperados
            if agentes:
                assert 'id' in agentes[0]
                assert 'nombre' in agentes[0]
                assert 'apellido' in agentes[0]
    
    def test_get_agent_with_least_incidents(self, app, init_database):
        """Prueba la obtención del agente con menos incidencias."""
        with app.app_context():
            # Crear una instancia del servicio
            service = AssignmentService()
            
            # Ejecutar el método a probar
            agente_id = service.get_agent_with_least_incidents()
            
            # Verificar que se haya recuperado un ID de agente
            assert agente_id is not None
            assert isinstance(agente_id, int)
    
    @patch('app.services.assignment_service.AssignmentService.get_available_agents')
    def test_assign_agent_with_available_agents(self, mock_get_available_agents, app):
        """Prueba la asignación de un agente cuando hay agentes disponibles."""
        # Simular agentes disponibles
        mock_get_available_agents.return_value = [
            {'id': 2, 'nombre': 'Agente', 'apellido': 'Prueba'}
        ]
        
        # Crear una instancia del servicio
        service = AssignmentService()
        
        # Ejecutar el método a probar
        agente_id = service.assign_agent()
        
        # Verificar que se haya asignado al agente esperado
        assert agente_id == 2
    
    @patch('app.services.assignment_service.AssignmentService.get_available_agents')
    @patch('app.services.assignment_service.AssignmentService.get_agent_with_least_incidents')
    def test_assign_agent_without_available_agents(self, mock_get_agent_with_least_incidents, mock_get_available_agents, app):
        """Prueba la asignación de un agente cuando no hay agentes disponibles."""
        # Simular que no hay agentes disponibles
        mock_get_available_agents.return_value = []
        mock_get_agent_with_least_incidents.return_value = 2
        
        # Crear una instancia del servicio
        service = AssignmentService()
        
        # Ejecutar el método a probar
        agente_id = service.assign_agent()
        
        # Verificar que se haya asignado al agente con menos incidencias
        assert agente_id == 2
    
    @patch('app.services.assignment_service.AssignmentService.get_available_agents')
    @patch('app.services.assignment_service.AssignmentService.get_agent_with_least_incidents')
    def test_assign_agent_no_agents_available(self, mock_get_agent_with_least_incidents, mock_get_available_agents, app):
        """Prueba el comportamiento cuando no hay agentes disponibles de ningún tipo."""
        # Simular que no hay agentes disponibles ni con menos incidencias
        mock_get_available_agents.return_value = []
        mock_get_agent_with_least_incidents.return_value = None
        
        # Crear una instancia del servicio
        service = AssignmentService()
        
        # El método debe lanzar una excepción
        with pytest.raises(ValueError) as e:
            service.assign_agent()
        
        # Verificar el mensaje de error
        assert "No hay agentes disponibles" in str(e.value)

class TestNotificationService:
    """Pruebas para el servicio de notificaciones."""
    
    def test_get_user_email_by_incident(self, app, init_database):
        """Prueba la obtención del correo del usuario por incidencia."""
        with app.app_context():
            db = init_database
            
            # Obtener un usuario
            user = Usuario.find_by_email('usuario@sistema.com')
            
            # Crear una incidencia para el usuario
            incidencia = Incidencia(
                titulo='Incidencia para notificación',
                descripcion='Descripción para notificación',
                categoria_id=1,
                prioridad_id=2,
                estado_id=1,
                usuario_creador_id=user.id,
                fecha_creacion=datetime.now()
            )
            db.session.add(incidencia)
            db.session.commit()
            
            incidencia_id = incidencia.id
            
            # Crear una instancia del servicio
            service = NotificationService()
            
            # Ejecutar el método a probar
            email = service.get_user_email_by_incident(incidencia_id)
            
            # Verificar que se haya recuperado el correo correctamente
            assert email == 'usuario@sistema.com'
    
    @patch('app.services.mail_service.send_email')
    def test_notify_status_change(self, mock_send_email, app, init_database):
        """Prueba la notificación de cambio de estado."""
        # Simular el método send_email
        mock_send_email.return_value = True
        
        with app.app_context():
            db = init_database
            
            # Obtener un usuario
            user = Usuario.find_by_email('usuario@sistema.com')
            
            # Crear una incidencia para notificar
            incidencia = Incidencia(
                titulo='Incidencia para notificación',
                descripcion='Descripción para notificación',
                categoria_id=1,
                prioridad_id=2,
                estado_id=1,
                usuario_creador_id=user.id,
                fecha_creacion=datetime.now()
            )
            db.session.add(incidencia)
            db.session.commit()
            
            incidencia_id = incidencia.id
            
            # Crear una instancia del servicio
            service = NotificationService()
            
            # Ejecutar el método a probar
            result = service.notify_status_change(
                incidencia_id, 
                'En progreso', 
                'La incidencia ha sido asignada a un agente'
            )
            
            # Verificar que se haya notificado correctamente
            assert result is True
            
            # Verificar que se haya llamado al método send_email con los parámetros correctos
            mock_send_email.assert_called_once()
            args, _ = mock_send_email.call_args
            assert args[0] == 'usuario@sistema.com'  # Destinatario
            assert 'Actualización de su incidencia' in args[1]  # Asunto
            assert 'En progreso' in args[2]  # Cuerpo

class TestMailService:
    """Pruebas para el servicio de correo."""
    
    @patch('app.services.mail_service.mail.send')
    @patch('flask.current_app.config')
    def test_send_email(self, mock_config, mock_mail_send, app):
        """Prueba el envío de correo."""
        # Configurar los mocks
        mock_config.get.return_value = 'no-reply@sistema.com'
        
        with app.app_context():
            # Ejecutar el método a probar
            result = send_email(
                'destinatario@ejemplo.com',
                'Asunto de prueba',
                'Contenido de prueba'
            )
            
            # Verificar que se haya enviado correctamente
            assert result is True
            
            # Verificar que se haya llamado al método mail.send con los parámetros correctos
            mock_mail_send.assert_called_once()
    
    def test_send_email_invalid_params(self, app):
        """Prueba el envío de correo con parámetros inválidos."""
        with app.app_context():
            # Parámetros vacíos
            result = send_email('', 'Asunto', 'Contenido')
            assert result is False
            
            result = send_email('email@ejemplo.com', '', 'Contenido')
            assert result is False
            
            result = send_email('email@ejemplo.com', 'Asunto', '')
            assert result is False

class TestSMSService:
    """Pruebas para el servicio de SMS."""
    
    @patch('app.services.sms_service.Client')
    @patch('flask.current_app.config')
    def test_send_sms(self, mock_config, mock_client, app):
        """Prueba el envío de SMS."""
        from app.services.sms_service import send_sms
        
        # Configurar los mocks
        mock_config.get.side_effect = lambda key: {
            'TWILIO_ACCOUNT_SID': 'test_sid',
            'TWILIO_AUTH_TOKEN': 'test_token',
            'TWILIO_PHONE_NUMBER': '+1234567890'
        }.get(key)
        
        mock_client_instance = MagicMock()
        mock_client.return_value = mock_client_instance
        
        mock_messages = MagicMock()
        mock_client_instance.messages = mock_messages
        mock_messages.create.return_value = MagicMock()
        
        with app.app_context():
            # Ejecutar el método a probar
            result = send_sms('+9876543210', 'Mensaje de prueba')
            
            # Verificar que se haya enviado correctamente
            assert result is True
            
            # Verificar que se haya llamado al método messages.create con los parámetros correctos
            mock_messages.create.assert_called_once_with(
                body='Mensaje de prueba',
                from_='+1234567890',
                to='+9876543210'
            )
    
    def test_send_sms_invalid_params(self, app):
        """Prueba el envío de SMS con parámetros inválidos."""
        from app.services.sms_service import send_sms
        
        with app.app_context():
            # Parámetros vacíos
            result = send_sms('', 'Mensaje')
            assert result is False
            
            result = send_sms('+1234567890', '')
            assert result is False
        # Prueba la obtención del correo del usuario por