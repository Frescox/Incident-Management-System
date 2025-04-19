from flask import current_app, render_template, session, redirect, url_for, request, flash
from app.models.user import Usuario
from app.models.ticket_models import Incidencia, Comentario, HistorialEstado
from app.models.catalog_models import Estado, Prioridad, Categoria
from app.utils.aes_encryption import decrypt
from datetime import datetime

class AgentController:
    @staticmethod
    def dashboard():
        if 'user_email' not in session:
            return redirect(url_for('auth.index'))

        usuario = Usuario.find_by_email(session['user_email'])
        if not usuario or usuario.rol_id != 2:  # 2 = agent role
            return redirect(url_for('auth.index'))

        nombre = decrypt(usuario.nombre)
        apellido = decrypt(usuario.apellido)
        correo = session.get('user_email')
        
        # Obtener todas las incidencias asignadas al agente
        incidencias = Incidencia.get_by_agent(usuario.id)
        
        # Agrupar incidencias por estado
        nuevas = [inc for inc in incidencias if inc.estado_id == 1]  # Estado "nuevo"
        en_progreso = [inc for inc in incidencias if inc.estado_id == 2]  # Estado "en_progreso"
        resueltas = [inc for inc in incidencias if inc.estado_id == 3]  # Estado "resuelto"
        cerradas = [inc for inc in incidencias if inc.estado_id == 4]  # Estado "cerrado"
        
        # Obtener todos los estados para el formulario de cambio de estado
        estados = Estado.get_all()
        
        return render_template('agent_dashboard.html',
                            nombre=nombre,
                            apellido=apellido,
                            correo=correo,
                            nuevas=nuevas,
                            en_progreso=en_progreso,
                            resueltas=resueltas,
                            cerradas=cerradas,
                            estados=estados)

    @staticmethod
    def resolve_incident(incident_id):
        """Método para resolver directamente una incidencia"""
        if 'user_email' not in session:
            return redirect(url_for('auth.index'))

        usuario = Usuario.find_by_email(session['user_email'])
        if not usuario or usuario.rol_id != 2:
            return redirect(url_for('auth.index'))

        incidencia = Incidencia.get_by_id(incident_id)
        if not incidencia or incidencia.agente_asignado_id != usuario.id:
            flash('No tienes permiso para resolver esta incidencia', 'error')
            return redirect(url_for('agent.dashboard'))

        # Verificar que la incidencia esté en estado "en_progreso"
        if incidencia.estado_id != 2:  # 2 = en_progreso
            flash('Solo se pueden resolver incidencias en progreso', 'warning')
            return redirect(url_for('agent.dashboard'))

        # Cambiar al estado "resuelto" (ID 3)
        comentario = request.form.get('comentario', 'Incidencia resuelta')
        if incidencia.change_status(3, usuario.id, comentario):
            flash('Incidencia resuelta correctamente', 'success')
        else:
            flash('Error al resolver la incidencia', 'error')

        return redirect(url_for('agent.dashboard'))
    
    @staticmethod
    def list_incidents():
        if 'user_email' not in session:
            return redirect(url_for('auth.index'))

        usuario = Usuario.find_by_email(session['user_email'])
        if not usuario or usuario.rol_id != 2:
            return redirect(url_for('auth.index'))

        incidencias = Incidencia.get_by_agent(usuario.id)
        categorias = Categoria.get_all()
        estados = Estado.get_all()
        prioridades = Prioridad.get_all()

        return render_template('agent_incidents.html',
                            incidencias=incidencias,
                            categorias=categorias,
                            estados=estados,
                            prioridades=prioridades)

    @staticmethod
    def view_incident(incident_id):
        if 'user_email' not in session:
            return redirect(url_for('auth.index'))

        usuario = Usuario.find_by_email(session['user_email'])
        if not usuario or usuario.rol_id != 2:
            return redirect(url_for('auth.index'))

        incidencia = Incidencia.get_by_id_with_details(incident_id)
        if not incidencia or incidencia.agente_asignado_id != usuario.id:
            flash('No tienes permiso para ver esta incidencia', 'error')
            return redirect(url_for('auth.index'))

        comentarios = Comentario.get_by_incident(incident_id)
        historial = HistorialEstado.get_by_incident(incident_id)

        nombre = decrypt(usuario.nombre)
        apellido = decrypt(usuario.apellido)
        correo = session.get('user_email')
        
        # Verificar si el primer comentario tiene un usuario, y descifrar el nombre y apellido una sola vez
        if comentarios and comentarios[0].usuario:
            nombre_descifrado = decrypt(comentarios[0].usuario.nombre) if comentarios[0].usuario.nombre else None
            apellido_descifrado = decrypt(comentarios[0].usuario.apellido) if comentarios[0].usuario.apellido else None

            # Asignar el mismo nombre y apellido descifrado a todos los comentarios
            for comentario in comentarios:
                if comentario.usuario:
                    comentario.usuario.nombre = nombre_descifrado
                    comentario.usuario.apellido = apellido_descifrado

    # -------------------------------------------------------------------------

        return render_template('agent_view_incident.html',
                            nombre=nombre,
                            apellido=apellido,
                            correo=correo,
                            incidencia=incidencia,
                            comentarios=comentarios,
                            historial=historial)

    @staticmethod
    def update_incident(incident_id):
        if 'user_email' not in session:
            return redirect(url_for('auth.index'))

        usuario = Usuario.find_by_email(session['user_email'])
        incidencia = Incidencia.get_by_id(incident_id)

        if not usuario or not incidencia or incidencia.agente_asignado_id != usuario.id:
            flash('No tienes permiso para editar esta incidencia', 'error')
            return redirect(url_for('agent.dashboard'))

        if request.method == 'POST':
            estado_id = request.form.get('estado_id')
            comentario = request.form.get('comentario', '')

            if estado_id and int(estado_id) != incidencia.estado_id:
                if incidencia.change_status(int(estado_id), usuario.id, comentario):
                    flash('Estado actualizado correctamente', 'success')
                else:
                    flash('Error al cambiar el estado', 'error')
            else:
                flash('No se realizaron cambios', 'info')

        return redirect(url_for('view_incident', incident_id=incident_id))

    @staticmethod
    def assign_incident(incident_id):
        if 'user_email' not in session:
            return redirect(url_for('auth.index'))

        usuario = Usuario.find_by_email(session['user_email'])
        if not usuario or usuario.rol_id != 2:
            return redirect(url_for('auth.index'))

        incidencia = Incidencia.get_by_id(incident_id)
        if not incidencia:
            flash('Incidencia no encontrada', 'error')
            return redirect(url_for('agent.dashboard'))

        incidencia.agente_asignado_id = usuario.id
        incidencia.fecha_ultima_actualizacion = datetime.utcnow()
        
        if incidencia.save():
            flash('Incidencia asignada correctamente', 'success')
        else:
            flash('Error al asignar incidencia', 'error')

        return redirect(url_for('agent.view_incident', incident_id=incident_id))

    @staticmethod
    def change_status(incident_id):
        if 'user_email' not in session:
            return redirect(url_for('auth.index'))

        usuario = Usuario.find_by_email(session['user_email'])
        incidencia = Incidencia.get_by_id(incident_id)

        if not usuario or not incidencia or incidencia.agente_asignado_id != usuario.id:
            flash('No tienes permiso para cambiar el estado', 'error')
            return redirect(url_for('agent.dashboard'))

        if request.method == 'POST':
            estado_id = request.form.get('estado_id')
            comentario = request.form.get('comentario', '')

            if estado_id and int(estado_id) != incidencia.estado_id:
                if incidencia.change_status(int(estado_id), usuario.id):
                     # Enviar notificación al usuario
                    try:
                        from app.services.notification_service import NotificationService
                        notification_service = NotificationService()

                        # Aquí debes obtener el nombre o descripción del nuevo estado
                        nuevo_estado_nombre = incidencia.estado.nombre if incidencia.estado else "actualizado"
                        
                        notification_service.notify_status_change(incident_id, nuevo_estado_nombre, comentario)
                    except Exception as e:
                        current_app.logger.error(f"Error al enviar notificación: {str(e)}")
                    flash('Estado actualizado correctamente', 'success')
                else:
                    flash('Error al cambiar el estado', 'error')
            else:
                flash('No se realizaron cambios', 'info')

        return redirect(url_for('agent.dashboard', incident_id=incident_id))