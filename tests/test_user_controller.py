import pytest
from flask import session, url_for
from app.models.ticket_models import Incidencia, Comentario
from app.models.user_models import Usuario

class TestUserController:
    """Pruebas para el controlador de usuarios."""
    
    def test_dashboard_access(self, client, init_database):
        """Prueba el acceso al dashboard de usuario."""
        # Sin iniciar sesión, debe redirigir a la página de inicio
        response = client.get('/user/dashboard')
        assert response.status_code == 302  # Redirección
        
        # Iniciar sesión como usuario
        with client.session_transaction() as sess:
            # Simulamos haber iniciado sesión
            user = Usuario.find_by_email('usuario@sistema.com')
            sess['user_id'] = user.id
            sess['user_email'] = 'usuario@sistema.com'
            sess['user_role'] = user.rol_id
        
        # Ahora debe permitir el acceso
        response = client.get('/user/dashboard')
        assert response.status_code == 200
        assert b'Mis Incidencias' in response.data
    
    def test_create_incident(self, client, app, init_database):
        """Prueba la creación de una incidencia por parte del usuario."""
        # Iniciar sesión como usuario
        with client.session_transaction() as sess:
            user = Usuario.find_by_email('usuario@sistema.com')
            sess['user_id'] = user.id
            sess['user_email'] = 'usuario@sistema.com'
            sess['user_role'] = user.rol_id
        
        # Contar incidencias iniciales
        with app.app_context():
            initial_count = Incidencia.query.count() if hasattr(Incidencia, 'query') else 0
        
        # Crear una nueva incidencia
        response = client.post('/user/incidents/create', data={
            'titulo': 'Prueba Incidencia',
            'descripcion': 'Esta es una incidencia de prueba',
            'categoria_id': 1,  # Hardware
            'prioridad_id': 2   # Media
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'creada exitosamente' in response.data
        
        # Verificar que se haya creado la incidencia
        with app.app_context():
            current_count = Incidencia.query.count() if hasattr(Incidencia, 'query') else 0
            assert current_count > initial_count
            
            # Verificar que los datos sean correctos
            if hasattr(Incidencia, 'query'):
                incidencia = Incidencia.query.filter_by(titulo='Prueba Incidencia').first()
                assert incidencia is not None
                assert incidencia.titulo == 'Prueba Incidencia'
                assert incidencia.descripcion == 'Esta es una incidencia de prueba'
                assert incidencia.categoria_id == 1
                assert incidencia.prioridad_id == 2
                assert incidencia.usuario_creador_id == user.id
    
    def test_view_incident(self, client, app, init_database):
        """Prueba la visualización de una incidencia específica."""
        # Iniciar sesión como usuario
        with client.session_transaction() as sess:
            user = Usuario.find_by_email('usuario@sistema.com')
            sess['user_id'] = user.id
            sess['user_email'] = 'usuario@sistema.com'
            sess['user_role'] = user.rol_id
        
        # Crear una incidencia para visualizarla
        with app.app_context():
            # Crear una incidencia de prueba
            incidencia = Incidencia(
                titulo='Incidencia para Visualizar',
                descripcion='Esta incidencia es para probar la visualización',
                categoria_id=1,
                prioridad_id=2,
                estado_id=1,
                usuario_creador_id=user.id
            )
            db = init_database
            db.session.add(incidencia)
            db.session.commit()
            
            incidencia_id = incidencia.id
        
        # Ver la incidencia
        response = client.get(f'/user/incidents/{incidencia_id}')
        assert response.status_code == 200
        assert b'Incidencia para Visualizar' in response.data
    
    def test_update_incident(self, client, app, init_database):
        """Prueba la actualización de una incidencia."""
        # Iniciar sesión como usuario
        with client.session_transaction() as sess:
            user = Usuario.find_by_email('usuario@sistema.com')
            sess['user_id'] = user.id
            sess['user_email'] = 'usuario@sistema.com'
            sess['user_role'] = user.rol_id
        
        # Crear una incidencia para actualizarla
        with app.app_context():
            incidencia = Incidencia(
                titulo='Incidencia para Actualizar',
                descripcion='Esta incidencia es para probar la actualización',
                categoria_id=1,
                prioridad_id=2,
                estado_id=1,
                usuario_creador_id=user.id
            )
            db = init_database
            db.session.add(incidencia)
            db.session.commit()
            
            incidencia_id = incidencia.id
        
        # Actualizar la incidencia
        response = client.post(f'/user/incidents/{incidencia_id}/update', data={
            'titulo': 'Incidencia Actualizada',
            'descripcion': 'Esta descripción ha sido actualizada',
            'categoria_id': 2,  # Software
            'prioridad_id': 1   # Alta
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'actualizada exitosamente' in response.data
        
        # Verificar que se haya actualizado la incidencia
        with app.app_context():
            incidencia_actualizada = Incidencia.query.get(incidencia_id)
            assert incidencia_actualizada.titulo == 'Incidencia Actualizada'
            assert incidencia_actualizada.descripcion == 'Esta descripción ha sido actualizada'
            assert incidencia_actualizada.categoria_id == 2
            assert incidencia_actualizada.prioridad_id == 1
    
    def test_delete_incident(self, client, app, init_database):
        """Prueba la eliminación de una incidencia."""
        # Iniciar sesión como usuario
        with client.session_transaction() as sess:
            user = Usuario.find_by_email('usuario@sistema.com')
            sess['user_id'] = user.id
            sess['user_email'] = 'usuario@sistema.com'
            sess['user_role'] = user.rol_id
        
        # Crear una incidencia para eliminarla
        with app.app_context():
            incidencia = Incidencia(
                titulo='Incidencia para Eliminar',
                descripcion='Esta incidencia es para probar la eliminación',
                categoria_id=1,
                prioridad_id=2,
                estado_id=1,
                usuario_creador_id=user.id
            )
            db = init_database
            db.session.add(incidencia)
            db.session.commit()
            
            incidencia_id = incidencia.id
            
            # Verificar que la incidencia existe
            assert Incidencia.query.get(incidencia_id) is not None
        
        # Eliminar la incidencia
        response = client.post(f'/user/incidents/{incidencia_id}/delete', follow_redirects=True)
        
        assert response.status_code == 200
        assert b'eliminada exitosamente' in response.data
        
        # Verificar que la incidencia se haya eliminado
        with app.app_context():
            assert Incidencia.query.get(incidencia_id) is None
    
    def test_add_comment(self, client, app, init_database):
        """Prueba la adición de un comentario a una incidencia."""
        # Iniciar sesión como usuario
        with client.session_transaction() as sess:
            user = Usuario.find_by_email('usuario@sistema.com')
            sess['user_id'] = user.id
            sess['user_email'] = 'usuario@sistema.com'
            sess['user_role'] = user.rol_id
        
        # Crear una incidencia para comentar
        with app.app_context():
            incidencia = Incidencia(
                titulo='Incidencia para Comentar',
                descripcion='Esta incidencia es para probar los comentarios',
                categoria_id=1,
                prioridad_id=2,
                estado_id=1,
                usuario_creador_id=user.id
            )
            db = init_database
            db.session.add(incidencia)
            db.session.commit()
            
            incidencia_id = incidencia.id
            
            # Contar comentarios iniciales
            initial_comments = Comentario.query.filter_by(incidencia_id=incidencia_id).count()
        
        # Añadir un comentario
        response = client.post(f'/user/incidents/{incidencia_id}/comments', data={
            'comment': 'Este es un comentario de prueba'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'Comentario' in response.data
        
        # Verificar que se haya añadido el comentario
        with app.app_context():
            current_comments = Comentario.query.filter_by(incidencia_id=incidencia_id).count()
            assert current_comments > initial_comments
            
            # Verificar que el contenido sea correcto
            ultimo_comentario = Comentario.query.filter_by(incidencia_id=incidencia_id).order_by(Comentario.id.desc()).first()
            assert ultimo_comentario.contenido == 'Este es un comentario de prueba'
            assert ultimo_comentario.usuario_id == user.id