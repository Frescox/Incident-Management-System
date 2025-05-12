import pytest
from flask import session, url_for
from app.models.ticket_models import Incidencia, HistorialEstado
from app.models.user_models import Usuario
from app.models.catalog_models import Estado

class TestAgentController:
    """Pruebas para el controlador de agentes."""
    
    def test_agent_dashboard_access(self, client, init_database):
        """Prueba el acceso al dashboard de agente."""
        # Sin iniciar sesión, debe redirigir a la página de inicio
        response = client.get('/agent/dashboard')
        assert response.status_code == 302  # Redirección
        
        # Iniciar sesión como agente
        with client.session_transaction() as sess:
            # Simulamos haber iniciado sesión como agente
            agent = Usuario.find_by_email('agente@sistema.com')
            sess['user_id'] = agent.id
            sess['user_email'] = 'agente@sistema.com'
            sess['user_role'] = agent.rol_id
        
        # Ahora debe permitir el acceso
        response = client.get('/agent/dashboard')
        assert response.status_code == 200
        assert b'Nuevas Incidencias' in response.data
    
    def test_view_incident_as_agent(self, client, app, init_database):
        """Prueba la visualización de una incidencia como agente."""
        # Iniciar sesión como agente
        with client.session_transaction() as sess:
            agent = Usuario.find_by_email('agente@sistema.com')
            sess['user_id'] = agent.id
            sess['user_email'] = 'agente@sistema.com'
            sess['user_role'] = agent.rol_id
        
        # Crear una incidencia asignada al agente
        with app.app_context():
            # Buscar un usuario para ser el creador
            user = Usuario.find_by_email('usuario@sistema.com')
            
            # Crear una incidencia de prueba
            incidencia = Incidencia(
                titulo='Incidencia para Agente',
                descripcion='Esta incidencia es para probar la visualización como agente',
                categoria_id=1,
                prioridad_id=2,
                estado_id=1,
                usuario_creador_id=user.id,
                agente_asignado_id=agent.id
            )
            db = init_database
            db.session.add(incidencia)
            db.session.commit()
            
            incidencia_id = incidencia.id
        
        # Ver la incidencia
        response = client.get(f'/agent/incidents/{incidencia_id}')
        assert response.status_code == 200
        assert b'Incidencia para Agente' in response.data
    
    def test_change_incident_status(self, client, app, init_database):
        """Prueba el cambio de estado de una incidencia por un agente."""
        # Iniciar sesión como agente
        with client.session_transaction() as sess:
            agent = Usuario.find_by_email('agente@sistema.com')
            sess['user_id'] = agent.id
            sess['user_email'] = 'agente@sistema.com'
            sess['user_role'] = agent.rol_id
        
        # Crear una incidencia asignada al agente
        with app.app_context():
            user = Usuario.find_by_email('usuario@sistema.com')
            
            incidencia = Incidencia(
                titulo='Incidencia para Cambiar Estado',
                descripcion='Esta incidencia es para probar el cambio de estado',
                categoria_id=1,
                prioridad_id=2,
                estado_id=1,  # Nuevo
                usuario_creador_id=user.id,
                agente_asignado_id=agent.id
            )
            db = init_database
            db.session.add(incidencia)
            db.session.commit()
            
            incidencia_id = incidencia.id
            estado_inicial_id = incidencia.estado_id
            
            # Verificar el estado inicial
            assert incidencia.estado_id == 1  # Nuevo
        
        # Cambiar el estado a "en progreso"
        response = client.post(f'/agent/incidents/{incidencia_id}/status', data={
            'estado_id': 2,  # En progreso
            'comentario': 'Cambio a en progreso'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'Estado actualizado correctamente' in response.data
        
        # Verificar que el estado haya cambiado
        with app.app_context():
            incidencia_actualizada = Incidencia.query.get(incidencia_id)
            assert incidencia_actualizada.estado_id == 2  # En progreso
            
            # Verificar que se haya registrado en el historial
            historial = HistorialEstado.query.filter_by(incidencia_id=incidencia_id).first()
            assert historial is not None
            assert historial.estado_anterior_id == estado_inicial_id
            assert historial.estado_nuevo_id == 2
            assert historial.usuario_id == agent.id
    
    def test_resolve_incident(self, client, app, init_database):
        """Prueba la resolución de una incidencia por un agente."""
        # Iniciar sesión como agente
        with client.session_transaction() as sess:
            agent = Usuario.find_by_email('agente@sistema.com')
            sess['user_id'] = agent.id
            sess['user_email'] = 'agente@sistema.com'
            sess['user_role'] = agent.rol_id
        
        # Crear una incidencia en estado "en progreso"
        with app.app_context():
            user = Usuario.find_by_email('usuario@sistema.com')
            
            incidencia = Incidencia(
                titulo='Incidencia para Resolver',
                descripcion='Esta incidencia es para probar la resolución',
                categoria_id=1,
                prioridad_id=2,
                estado_id=2,  # En progreso
                usuario_creador_id=user.id,
                agente_asignado_id=agent.id
            )
            db = init_database
            db.session.add(incidencia)
            db.session.commit()
            
            incidencia_id = incidencia.id
        
        # Resolver la incidencia
        response = client.post(f'/agent/incidents/resolve/{incidencia_id}', data={
            'comentario': 'Incidencia resuelta con éxito'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'Incidencia resuelta correctamente' in response.data
        
        # Verificar que el estado haya cambiado a "resuelto"
        with app.app_context():
            incidencia_actualizada = Incidencia.query.get(incidencia_id)
            assert incidencia_actualizada.estado_id == 3  # Resuelto
            
            # Verificar que se haya establecido la fecha de resolución
            assert incidencia_actualizada.fecha_resolucion is not None
    
    def test_assign_incident(self, client, app, init_database):
        """Prueba la asignación de una incidencia a un agente."""
        # Iniciar sesión como agente
        with client.session_transaction() as sess:
            agent = Usuario.find_by_email('agente@sistema.com')
            sess['user_id'] = agent.id
            sess['user_email'] = 'agente@sistema.com'
            sess['user_role'] = agent.rol_id
        
        # Crear una incidencia sin agente asignado
        with app.app_context():
            user = Usuario.find_by_email('usuario@sistema.com')
            
            incidencia = Incidencia(
                titulo='Incidencia para Asignar',
                descripcion='Esta incidencia es para probar la asignación',
                categoria_id=1,
                prioridad_id=2,
                estado_id=1,  # Nuevo
                usuario_creador_id=user.id,
                agente_asignado_id=None  # Sin agente asignado
            )
            db = init_database
            db.session.add(incidencia)
            db.session.commit()
            
            incidencia_id = incidencia.id
        
        # Asignar la incidencia al agente actual
        response = client.post(f'/agent/incidents/assign/{incidencia_id}', follow_redirects=True)
        
        assert response.status_code == 200
        assert b'Incidencia asignada correctamente' in response.data
        
        # Verificar que la incidencia esté asignada al agente
        with app.app_context():
            incidencia_actualizada = Incidencia.query.get(incidencia_id)
            assert incidencia_actualizada.agente_asignado_id == agent.id
    
    def test_list_incidents(self, client, app, init_database):
        """Prueba el listado de incidencias asignadas a un agente."""
        # Iniciar sesión como agente
        with client.session_transaction() as sess:
            agent = Usuario.find_by_email('agente@sistema.com')
            sess['user_id'] = agent.id
            sess['user_email'] = 'agente@sistema.com'
            sess['user_role'] = agent.rol_id
        
        # Crear varias incidencias asignadas al agente
        with app.app_context():
            user = Usuario.find_by_email('usuario@sistema.com')
            db = init_database
            
            # Crear 3 incidencias
            for i in range(3):
                incidencia = Incidencia(
                    titulo=f'Incidencia de prueba {i+1}',
                    descripcion=f'Descripción de la incidencia {i+1}',
                    categoria_id=1,
                    prioridad_id=2,
                    estado_id=1,  # Nuevo
                    usuario_creador_id=user.id,
                    agente_asignado_id=agent.id
                )
                db.session.add(incidencia)
            
            db.session.commit()
        
        # Obtener el listado de incidencias
        response = client.get('/agent/incidents')
        
        assert response.status_code == 200
        assert b'Incidencia de prueba 1' in response.data
        assert b'Incidencia de prueba 2' in response.data
        assert b'Incidencia de prueba 3' in response.data