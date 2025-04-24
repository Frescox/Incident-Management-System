import pytest
from flask import session, url_for
from app.models.ticket_models import Incidencia
from app.models.user_models import Usuario
from app.utils.aes_encryption import encrypt, decrypt

class TestAdminController:
    """Pruebas para el controlador de administradores."""
    
    def test_admin_dashboard_access(self, client, init_database):
        """Prueba el acceso al dashboard de administrador."""
        # Sin iniciar sesión, debe redirigir a la página de inicio
        
        response = client.get(url_for('/admin/login'))         
        assert response.status_code == 302
        
        # Iniciar sesión como administrador
        with client.session_transaction() as sess:
            admin = Usuario.find_by_email('admin@sistema.com')
            sess['user_id'] = admin.id
            sess['user_email'] = 'admin@sistema.com'
            sess['user_role'] = admin.rol_id
        
        # Ahora debe permitir el acceso
        response = client.get(url_for('/admin/dashboard'))         
        assert response.status_code == 200
        assert b'Estadisticas' in response.data
        assert b'Usuarios Registrados' in response.data
    
    def test_view_incident_as_admin(self, client, app, init_database):
        """Prueba la visualización de una incidencia como administrador."""
        # Iniciar sesión como administrador
        with client.session_transaction() as sess:
            admin = Usuario.find_by_email('admin@sistema.com')
            sess['user_id'] = admin.id
            sess['user_email'] = 'admin@sistema.com'
            sess['user_role'] = admin.rol_id
        
        # Crear una incidencia para visualizarla
        with app.app_context():
            user = Usuario.find_by_email('usuario@sistema.com')
            agent = Usuario.find_by_email('agente@sistema.com')
            
            incidencia = Incidencia(
                titulo='Incidencia para Admin',
                descripcion='Esta incidencia es para probar la visualización como admin',
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
        response = client.get(f'/admin/incidents/{incidencia_id}')
        assert response.status_code == 200
        assert b'Incidencia para Admin' in response.data
    
    def test_update_user_role(self, client, app, init_database):
        """Prueba la actualización del rol de un usuario por un administrador."""
        # Iniciar sesión como administrador
        with client.session_transaction() as sess:
            admin = Usuario.find_by_email('admin@sistema.com')
            sess['user_id'] = admin.id
            sess['user_email'] = 'admin@sistema.com'
            sess['user_role'] = admin.rol_id
        
        # Obtener un usuario para cambiarle el rol
        with app.app_context():
            user = Usuario.find_by_email('usuario@sistema.com')
            user_id = user.id
            
            # Verificar el rol inicial
            assert user.rol_id == 3  # Usuario regular
        
        # Cambiar el rol a agente
        response = client.post(f'/admin/users/{user_id}/update_role', data={
            'rol_id': 2  # Agente
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'Rol actualizado correctamente' in response.data
        
        # Verificar que el rol haya cambiado
        with app.app_context():
            user_actualizado = Usuario.find_by_id(user_id)
            assert user_actualizado.rol_id == 2  # Ahora es agente
    
    def test_toggle_user_status(self, client, app, init_database):
        """Prueba la activación/desactivación de un usuario por un administrador."""
        # Iniciar sesión como administrador
        with client.session_transaction() as sess:
            admin = Usuario.find_by_email('admin@sistema.com')
            sess['user_id'] = admin.id
            sess['user_email'] = 'admin@sistema.com'
            sess['user_role'] = admin.rol_id
        
        # Obtener un usuario para cambiarle el estado
        with app.app_context():
            user = Usuario.find_by_email('usuario@sistema.com')
            user_id = user.id
            
            # Verificar el estado inicial
            assert user.estado is True  # Activo
        
        # Desactivar el usuario
        response = client.post(f'/admin/users/{user_id}/toggle_status', follow_redirects=True)
        
        assert response.status_code == 200
        assert b'Usuario desactivado correctamente' in response.data
        
        # Verificar que el estado haya cambiado
        with app.app_context():
            user_actualizado = Usuario.find_by_id(user_id)
            assert user_actualizado.estado is False  # Ahora está desactivado
        
        # Volver a activar el usuario
        response = client.post(f'/admin/users/{user_id}/toggle_status', follow_redirects=True)
        
        assert response.status_code == 200
        assert b'Usuario activado correctamente' in response.data
        
        # Verificar que el estado haya vuelto a cambiar
        with app.app_context():
            user_actualizado = Usuario.find_by_id(user_id)
            assert user_actualizado.estado is True  # Ahora está activo de nuevo
    
    def test_view_logs(self, client, app, init_database):
        """Prueba la visualización de logs de actividad."""
        # Iniciar sesión como administrador
        with client.session_transaction() as sess:
            admin = Usuario.find_by_email('admin@sistema.com')
            sess['user_id'] = admin.id
            sess['user_email'] = 'admin@sistema.com'
            sess['user_role'] = admin.rol_id
        
        # Acceder a la vista de logs
        response = client.get('/admin/logs/view')
        
        assert response.status_code == 200
        # La página de logs debería mostrar al menos el título
        assert b'Logs' in response.data
    
    def test_general_report(self, client, app, init_database):
        """Prueba la generación del reporte general."""
        # Iniciar sesión como administrador
        with client.session_transaction() as sess:
            admin = Usuario.find_by_email('admin@sistema.com')
            sess['user_id'] = admin.id
            sess['user_email'] = 'admin@sistema.com'
            sess['user_role'] = admin.rol_id
        
        # Crear algunas incidencias para el reporte
        with app.app_context():
            db = init_database
            user = Usuario.find_by_email('usuario@sistema.com')
            agent = Usuario.find_by_email('agente@sistema.com')
            
            # Crear incidencias con diferentes estados y categorías
            for i in range(5):
                incidencia = Incidencia(
                    titulo=f'Incidencia {i}',
                    descripcion=f'Descripción {i}',
                    categoria_id=(i % 3) + 1,  # Alternar entre categorías 1, 2 y 3
                    prioridad_id=(i % 3) + 1,  # Alternar entre prioridades 1, 2 y 3
                    estado_id=(i % 4) + 1,     # Alternar entre estados 1, 2, 3 y 4
                    usuario_creador_id=user.id,
                    agente_asignado_id=agent.id
                )
                db.session.add(incidencia)
            
            db.session.commit()
        
        # Acceder al reporte general
        response = client.get('/admin/general_report')
        
        assert response.status_code == 200
        
        # Debe devolver un JSON con datos para los gráficos
        json_data = response.get_json()
        assert 'estado_data' in json_data
        assert 'categoria_data' in json_data
        assert 'prioridad_data' in json_data
        assert 'roles_data' in json_data
        
        # Verificar que las listas de datos no estén vacías
        assert len(json_data['estado_data']) > 0
        assert len(json_data['categoria_data']) > 0
        assert len(json_data['prioridad_data']) > 0
        assert len(json_data['roles_data']) > 0