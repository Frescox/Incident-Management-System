from flask import render_template, session, redirect, url_for, request, flash
from flask import current_app
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
        
        # Get agent's assigned incidents
        incidencias = Incidencia.get_by_agent(usuario.id)
        estados = Estado.get_all()
        
        return render_template('agent_dashboard.html',
                            nombre=nombre,
                            apellido=apellido,
                            correo=correo,
                            incidencias=incidencias,
                            estados=estados)

    @staticmethod
    def list_incidents():
        if 'user_id' not in session:
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
            return redirect(url_for('agent.dashboard'))

        comentarios = Comentario.get_by_incident(incident_id)
        historial = HistorialEstado.get_by_incident(incident_id)

        return render_template('agent_view_incident.html',
                            incidencia=incidencia,
                            comentarios=comentarios,
                            historial=historial)

    @staticmethod
    def update_incident(incident_id):
        if 'user_id' not in session:
            return redirect(url_for('auth.index'))

        usuario = Usuario.find_by_email(session['user_email'])
        incidencia = Incidencia.get_by_id(incident_id)

        if not usuario or not incidencia or incidencia.agente_asignado_id != usuario.id:
            flash('No tienes permiso para editar esta incidencia', 'error')
            return redirect(url_for('agent.dashboard'))

        if request.method == 'POST':
            estado_id = request.form.get('estado_id')
            comentario = request.form.get('comentario', '')

            if estado_id and estado_id != incidencia.estado_id:
                incidencia.change_status(estado_id, usuario.id, comentario)
                flash('Estado actualizado correctamente', 'success')
            else:
                flash('No se realizaron cambios', 'info')

        return redirect(url_for('agent.view_incident', incident_id=incident_id))

    @staticmethod
    def assign_incident(incident_id):
        if 'user_id' not in session:
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
        if 'user_id' not in session:
            return redirect(url_for('auth.index'))

        usuario = Usuario.find_by_email(session['user_email'])
        incidencia = Incidencia.get_by_id(incident_id)

        if not usuario or not incidencia or incidencia.agente_asignado_id != usuario.id:
            flash('No tienes permiso para cambiar el estado', 'error')
            return redirect(url_for('agent.dashboard'))

        if request.method == 'POST':
            estado_id = request.form.get('estado_id')
            comentario = request.form.get('comentario', '')

            if estado_id and estado_id != incidencia.estado_id:

                incidencia.change_status(estado_id, usuario.id, comentario)

                # Enviar notificación al usuario
                try:
                    from app.services.notification_service import NotificationService
                    notification_service = NotificationService()

                    # Aquí debes obtener el nombre o descripción del nuevo estado
                    nuevo_estado_nombre = incidencia.estado.nombre if incidencia.estado else "actualizado"
                    
                    notification_service.notify_status_change(incident_id, nuevo_estado_nombre)
                except Exception as e:
                    current_app.logger.error(f"Error al enviar notificación: {str(e)}")

                flash('Estado actualizado correctamente', 'success')
            else:
                flash('No se realizaron cambios', 'info')

        return redirect(url_for('agent.view_incident', incident_id=incident_id))

    @staticmethod
    def add_comment(incident_id):
        if 'user_id' not in session:
            return redirect(url_for('auth.index'))

        usuario = Usuario.find_by_email(session['user_email'])
        incidencia = Incidencia.get_by_id(incident_id)

        if not usuario or not incidencia or incidencia.agente_asignado_id != usuario.id:
            flash('No tienes permiso para comentar', 'error')
            return redirect(url_for('agent.dashboard'))

        if request.method == 'POST':
            contenido = request.form.get('comment')
            if contenido:
                comentario = Comentario(
                    incidencia_id=incident_id,
                    usuario_id=usuario.id,
                    contenido=contenido
                )
                if comentario.save():
                    flash('Comentario añadido', 'success')
                else:
                    flash('Error al comentar', 'error')

        return redirect(url_for('agent.view_incident', incident_id=incident_id))