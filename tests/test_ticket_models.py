import pytest
from datetime import datetime
from app.models.ticket_models import Incidencia, Comentario, HistorialEstado
from app.models.user_models import Usuario
from app.models.catalog_models import Estado, Categoria, Prioridad

class TestIncidenciaModel:
    """Pruebas para el modelo Incidencia."""
    
    def test_create_incidencia(self, app, init_database):
        """Prueba la creación de una incidencia."""
        with app.app_context():
            # Obtener usuarios, categoría, prioridad y estado
            user = Usuario.find_by_email('usuario@sistema.com')
            agent = Usuario.find_by_email('agente@sistema.com')
            categoria = Categoria.query.filter_by(nombre='Hardware').first()
            prioridad = Prioridad.query.filter_by(nombre='alta').first()
            estado = Estado.query.filter_by(nombre='nuevo').first()
            
            # Crear una nueva incidencia
            nueva_incidencia = Incidencia(
                titulo='Prueba de Incidencia',
                descripcion='Esta es una descripción de prueba',
                categoria_id=categoria.id,
                prioridad_id=prioridad.id,
                estado_id=estado.id,
                usuario_creador_id=user.id,
                agente_asignado_id=agent.id,
                fecha_creacion=datetime.utcnow()
            )
            
            # Guardar la incidencia
            db = init_database
            db.session.add(nueva_incidencia)
            db.session.commit()
            
            incidencia_id = nueva_incidencia.id
            
            # Verificar que la incidencia se haya guardado correctamente
            incidencia_recuperada = Incidencia.query.get(incidencia_id)
            assert incidencia_recuperada is not None
            assert incidencia_recuperada.titulo == 'Prueba de Incidencia'
            assert incidencia_recuperada.descripcion == 'Esta es una descripción de prueba'
            assert incidencia_recuperada.categoria_id == categoria.id
            assert incidencia_recuperada.prioridad_id == prioridad.id
            assert incidencia_recuperada.estado_id == estado.id
            assert incidencia_recuperada.usuario_creador_id == user.id
            assert incidencia_recuperada.agente_asignado_id == agent.id
    
    def test_get_by_user(self, app, init_database):
        """Prueba la obtención de incidencias por usuario."""
        with app.app_context():
            # Obtener un usuario
            user = Usuario.find_by_email('usuario@sistema.com')
            
            # Crear varias incidencias para el usuario
            db = init_database
            for i in range(3):
                incidencia = Incidencia(
                    titulo=f'Incidencia de usuario {i+1}',
                    descripcion=f'Descripción {i+1}',
                    categoria_id=1,
                    prioridad_id=2,
                    estado_id=1,
                    usuario_creador_id=user.id,
                    fecha_creacion=datetime.utcnow()
                )
                db.session.add(incidencia)
            
            db.session.commit()
            
            # Obtener las incidencias del usuario
            incidencias = Incidencia.get_by_user(user.id)
            
            # Verificar que se hayan recuperado las incidencias
            assert len(incidencias) >= 3
            
            # Verificar que todas pertenezcan al usuario
            for inc in incidencias:
                assert inc.usuario_creador_id == user.id
    
    def test_get_by_agent(self, app, init_database):
        """Prueba la obtención de incidencias por agente."""
        with app.app_context():
            # Obtener un agente
            agent = Usuario.find_by_email('agente@sistema.com')
            
            # Crear varias incidencias asignadas al agente
            db = init_database
            for i in range(3):
                incidencia = Incidencia(
                    titulo=f'Incidencia de agente {i+1}',
                    descripcion=f'Descripción {i+1}',
                    categoria_id=1,
                    prioridad_id=2,
                    estado_id=1,
                    usuario_creador_id=1,  # Usuario cualquiera
                    agente_asignado_id=agent.id,
                    fecha_creacion=datetime.utcnow()
                )
                db.session.add(incidencia)
            
            db.session.commit()
            
            # Obtener las incidencias del agente
            incidencias = Incidencia.get_by_agent(agent.id)
            
            # Verificar que se hayan recuperado las incidencias
            assert len(incidencias) >= 3
            
            # Verificar que todas estén asignadas al agente
            for inc in incidencias:
                assert inc.agente_asignado_id == agent.id
    
    def test_change_status(self, app, init_database):
        """Prueba el cambio de estado de una incidencia."""
        with app.app_context():
            db = init_database
            
            # Crear una incidencia en estado "nuevo"
            incidencia = Incidencia(
                titulo='Incidencia para cambio de estado',
                descripcion='Descripción para cambio de estado',
                categoria_id=1,
                prioridad_id=2,
                estado_id=1,  # Nuevo
                usuario_creador_id=1,
                fecha_creacion=datetime.utcnow()
            )
            db.session.add(incidencia)
            db.session.commit()
            
            incidencia_id = incidencia.id
            usuario_id = 2  # ID de un usuario existente
            
            # Cambiar al estado "en progreso"
            resultado = incidencia.change_status(2, usuario_id, "Cambiado a en progreso")
            
            # Verificar que el cambio se haya realizado correctamente
            assert resultado is True
            
            # Recargar la incidencia
            incidencia = Incidencia.query.get(incidencia_id)
            assert incidencia.estado_id == 2  # En progreso
            
            # Verificar que se haya registrado en el historial
            historial = HistorialEstado.query.filter_by(incidencia_id=incidencia_id).first()
            assert historial is not None
            assert historial.estado_anterior_id == 1  # Nuevo
            assert historial.estado_nuevo_id == 2     # En progreso
            assert historial.usuario_id == usuario_id
            assert historial.comentario == "Cambiado a en progreso"
    
    def test_change_to_resolved_status(self, app, init_database):
        """Prueba el cambio a estado resuelto establece la fecha de resolución."""
        with app.app_context():
            db = init_database
            
            # Crear una incidencia en estado "en progreso"
            incidencia = Incidencia(
                titulo='Incidencia para resolución',
                descripcion='Descripción para resolución',
                categoria_id=1,
                prioridad_id=2,
                estado_id=2,  # En progreso
                usuario_creador_id=1,
                fecha_creacion=datetime.utcnow()
            )
            db.session.add(incidencia)
            db.session.commit()
            
            incidencia_id = incidencia.id
            
            # Verificar que no tiene fecha de resolución
            assert incidencia.fecha_resolucion is None
            
            # Cambiar al estado "resuelto"
            resultado = incidencia.change_status(3, 2, "Incidencia resuelta")
            
            # Verificar que el cambio se haya realizado correctamente
            assert resultado is True
            
            # Recargar la incidencia
            incidencia = Incidencia.query.get(incidencia_id)
            assert incidencia.estado_id == 3  # Resuelto
            
            # Verificar que se haya establecido la fecha de resolución
            assert incidencia.fecha_resolucion is not None
    
    def test_change_to_closed_status(self, app, init_database):
        """Prueba el cambio a estado cerrado establece la fecha de cierre."""
        with app.app_context():
            db = init_database
            
            # Crear una incidencia en estado "resuelto"
            incidencia = Incidencia(
                titulo='Incidencia para cierre',
                descripcion='Descripción para cierre',
                categoria_id=1,
                prioridad_id=2,
                estado_id=3,  # Resuelto
                usuario_creador_id=1,
                fecha_creacion=datetime.utcnow()
            )
            db.session.add(incidencia)
            db.session.commit()
            
            incidencia_id = incidencia.id
            
            # Verificar que no tiene fecha de cierre
            assert incidencia.fecha_cierre is None
            
            # Cambiar al estado "cerrado"
            resultado = incidencia.change_status(4, 2, "Incidencia cerrada")
            
            # Verificar que el cambio se haya realizado correctamente
            assert resultado is True
            
            # Recargar la incidencia
            incidencia = Incidencia.query.get(incidencia_id)
            assert incidencia.estado_id == 4  # Cerrado
            
            # Verificar que se haya establecido la fecha de cierre
            assert incidencia.fecha_cierre is not None
    
    def test_get_by_id_with_details(self, app, init_database):
        """Prueba la obtención de una incidencia con detalles relacionados."""
        with app.app_context():
            db = init_database
            
            # Obtener usuarios, categoría, prioridad y estado
            user = Usuario.find_by_email('usuario@sistema.com')
            agent = Usuario.find_by_email('agente@sistema.com')
            
            # Crear una incidencia
            incidencia = Incidencia(
                titulo='Incidencia con detalles',
                descripcion='Descripción con detalles',
                categoria_id=1,
                prioridad_id=2,
                estado_id=1,
                usuario_creador_id=user.id,
                agente_asignado_id=agent.id,
                fecha_creacion=datetime.utcnow()
            )
            db.session.add(incidencia)
            db.session.commit()
            
            incidencia_id = incidencia.id
            
            # Obtener la incidencia con detalles
            incidencia_con_detalles = Incidencia.get_by_id_with_details(incidencia_id)
            
            # Verificar que se haya recuperado correctamente
            assert incidencia_con_detalles is not None
            assert incidencia_con_detalles.id == incidencia_id
            
            # Verificar que se hayan cargado las relaciones
            assert incidencia_con_detalles.categoria is not None
            assert incidencia_con_detalles.prioridad is not None
            assert incidencia_con_detalles.estado is not None
            assert incidencia_con_detalles.creador is not None
            assert incidencia_con_detalles.asignado_a is not None

class TestComentarioModel:
    """Pruebas para el modelo Comentario."""
    
    def test_create_comentario(self, app, init_database):
        """Prueba la creación de un comentario."""
        with app.app_context():
            db = init_database
            
            # Obtener un usuario y una incidencia
            user = Usuario.find_by_email('usuario@sistema.com')
            
            # Crear una incidencia para comentar
            incidencia = Incidencia(
                titulo='Incidencia para comentar',
                descripcion='Descripción para comentar',
                categoria_id=1,
                prioridad_id=2,
                estado_id=1,
                usuario_creador_id=user.id,
                fecha_creacion=datetime.utcnow()
            )
            db.session.add(incidencia)
            db.session.commit()
            
            incidencia_id = incidencia.id
            
            # Crear un comentario
            comentario = Comentario(
                incidencia_id=incidencia_id,
                usuario_id=user.id,
                contenido='Este es un comentario de prueba',
                fecha_creacion=datetime.utcnow()
            )
            db.session.add(comentario)
            db.session.commit()
            
            comentario_id = comentario.id
            
            # Verificar que el comentario se haya guardado correctamente
            comentario_recuperado = Comentario.query.get(comentario_id)
            assert comentario_recuperado is not None
            assert comentario_recuperado.incidencia_id == incidencia_id
            assert comentario_recuperado.usuario_id == user.id
            assert comentario_recuperado.contenido == 'Este es un comentario de prueba'
    
    def test_get_by_incident(self, app, init_database):
        """Prueba la obtención de comentarios por incidencia."""
        with app.app_context():
            db = init_database
            
            # Obtener un usuario
            user = Usuario.find_by_email('usuario@sistema.com')
            
            # Crear una incidencia para comentar
            incidencia = Incidencia(
                titulo='Incidencia para comentarios',
                descripcion='Descripción para comentarios',
                categoria_id=1,
                prioridad_id=2,
                estado_id=1,
                usuario_creador_id=user.id,
                fecha_creacion=datetime.utcnow()
            )
            db.session.add(incidencia)
            db.session.commit()
            
            incidencia_id = incidencia.id
            
            # Crear varios comentarios para la incidencia
            for i in range(3):
                comentario = Comentario(
                    incidencia_id=incidencia_id,
                    usuario_id=user.id,
                    contenido=f'Comentario {i+1}',
                    fecha_creacion=datetime.utcnow()
                )
                db.session.add(comentario)
            
            db.session.commit()
            
            # Obtener los comentarios de la incidencia
            comentarios = Comentario.get_by_incident(incidencia_id)
            
            # Verificar que se hayan recuperado los comentarios
            assert len(comentarios) >= 3
            
            # Verificar que todos pertenezcan a la incidencia
            for com in comentarios:
                assert com.incidencia_id == incidencia_id

class TestHistorialEstadoModel:
    """Pruebas para el modelo HistorialEstado."""
    
    def test_create_historial(self, app, init_database):
        """Prueba la creación de un registro de historial de estado."""
        with app.app_context():
            db = init_database
            
            # Obtener un usuario y crear una incidencia
            user = Usuario.find_by_email('usuario@sistema.com')
            
            incidencia = Incidencia(
                titulo='Incidencia para historial',
                descripcion='Descripción para historial',
                categoria_id=1,
                prioridad_id=2,
                estado_id=1,
                usuario_creador_id=user.id,
                fecha_creacion=datetime.utcnow()
            )
            db.session.add(incidencia)
            db.session.commit()
            
            incidencia_id = incidencia.id
            
            # Crear un registro de historial
            historial = HistorialEstado(
                incidencia_id=incidencia_id,
                estado_anterior_id=1,  # Nuevo
                estado_nuevo_id=2,     # En progreso
                usuario_id=user.id,
                comentario='Cambio de estado manual',
                created_at=datetime.utcnow()
            )
            db.session.add(historial)
            db.session.commit()
            
            historial_id = historial.id
            
            # Verificar que el historial se haya guardado correctamente
            historial_recuperado = HistorialEstado.query.get(historial_id)
            assert historial_recuperado is not None
            assert historial_recuperado.incidencia_id == incidencia_id
            assert historial_recuperado.estado_anterior_id == 1
            assert historial_recuperado.estado_nuevo_id == 2
            assert historial_recuperado.usuario_id == user.id
            assert historial_recuperado.comentario == 'Cambio de estado manual'
    
    def test_get_by_incident(self, app, init_database):
        """Prueba la obtención del historial de estados por incidencia."""
        with app.app_context():
            db = init_database
            
            # Obtener un usuario y crear una incidencia
            user = Usuario.find_by_email('usuario@sistema.com')
            
            incidencia = Incidencia(
                titulo='Incidencia para historial múltiple',
                descripcion='Descripción para historial múltiple',
                categoria_id=1,
                prioridad_id=2,
                estado_id=1,
                usuario_creador_id=user.id,
                fecha_creacion=datetime.utcnow()
            )
            db.session.add(incidencia)
            db.session.commit()
            
            incidencia_id = incidencia.id
            
            # Crear varios registros de historial
            estados = [(1, 2), (2, 3), (3, 4)]  # (anterior, nuevo)
            for anterior, nuevo in estados:
                historial = HistorialEstado(
                    incidencia_id=incidencia_id,
                    estado_anterior_id=anterior,
                    estado_nuevo_id=nuevo,
                    usuario_id=user.id,
                    comentario=f'Cambio de {anterior} a {nuevo}',
                    created_at=datetime.utcnow()
                )
                db.session.add(historial)
            
            db.session.commit()
            
            # Obtener el historial de la incidencia
            historial_lista = HistorialEstado.get_by_incident(incidencia_id)
            
            # Verificar que se hayan recuperado los registros
            assert len(historial_lista) >= 3
            
            # Verificar que todos pertenezcan a la incidencia
            for hist in historial_lista:
                assert hist.incidencia_id == incidencia_id
            
            # Verificar que estén ordenados por fecha de creación descendente
            for i in range(len(historial_lista) - 1):
                assert historial_lista[i].created_at >= historial_lista[i+1].created_at