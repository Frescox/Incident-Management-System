from flask import render_template, session, redirect, url_for, request, flash, jsonify
from app.models.user_models import Usuario
from app.models.ticket_models import Incidencia, Comentario, HistorialEstado
from app.models.catalog_models import Estado, Prioridad, Categoria
from app.services.assignment_service import AssignmentService
from app.services.notification_service import NotificationService
from app.utils.aes_encryption import decrypt
from datetime import datetime
from app.models import db 
from sqlalchemy import text
from app.utils.logger import log_action


class UserController:
    @staticmethod
    def dashboard():
        if 'user_email' not in session:
            return redirect(url_for('auth.index'))

        usuario = Usuario.find_by_email(session['user_email'])
        if not usuario or usuario.rol_id != 3:
            return redirect(url_for('auth.index'))

        nombre = decrypt(usuario.nombre)
        apellido = decrypt(usuario.apellido)
        correo = session.get('user_email')
        
        incidencias = db.session.query(Incidencia).filter_by(
            usuario_creador_id=usuario.id
        ).join(
            Estado, Incidencia.estado_id == Estado.id
        ).join(
            Prioridad, Incidencia.prioridad_id == Prioridad.id
        ).join(
            Categoria, Incidencia.categoria_id == Categoria.id
        ).add_columns(
            Incidencia.id,
            Incidencia.titulo,
            Incidencia.descripcion,
            Incidencia.fecha_creacion,
            Estado.nombre.label('estado_nombre'),
            Prioridad.nombre.label('prioridad_nombre'),
            Categoria.nombre.label('categoria_nombre')
        ).order_by(
            Incidencia.fecha_creacion.desc()
        ).all()

        # Debug prints para verificar datos
        print("Categorías:", Categoria.query.all())
        print("Prioridades:", Prioridad.query.all())
        
        estados = Estado.query.all()
        prioridades = Prioridad.query.all()
        categorias = Categoria.query.all()

        return render_template('user_dashboard.html',
                            nombre=nombre,
                            apellido=apellido,
                            correo=correo,
                            incidencias=incidencias,
                            estados=estados,
                            prioridades=prioridades,
                            categorias=categorias)

    @staticmethod
    def create_incident():
        if 'user_id' not in session:
            return redirect(url_for('auth.index'))

        if request.method == 'POST':
            titulo = request.form.get('titulo')
            descripcion = request.form.get('descripcion')
            categoria_id = request.form.get('categoria_id')
            prioridad_id = request.form.get('prioridad_id')

            if not all([titulo, descripcion, categoria_id, prioridad_id]):
                flash('Todos los campos son requeridos', 'error')
                return redirect(url_for('user.dashboard'))
            
            assignment_service = AssignmentService()

            try:
                agente_asignado_id = assignment_service.assign_agent()
            except ValueError as e:
                flash(str(e), 'error')
                return redirect(url_for('user.dashboard'))
            

            nueva_incidencia = Incidencia(
                titulo=titulo,
                descripcion=descripcion,
                categoria_id=categoria_id,
                prioridad_id=prioridad_id,
                estado_id=1,  # Estado "nuevo"
                usuario_creador_id=session['user_id'],
                fecha_creacion=datetime.utcnow(),
                fecha_ultima_actualizacion=datetime.utcnow(),
                agente_asignado_id=agente_asignado_id
            )

            db.session.add(nueva_incidencia)
            try:
                db.session.commit()
                flash('Incidencia creada exitosamente', 'success')
                
                log_action(
                    usuario_id=session['user_id'],
                    accion="crear",
                     entidad="incidencia",
                    entidad_id=nueva_incidencia.id,
                    detalles=f"Incidencia '{titulo}' creada por el usuario",
                    user_agent=request.headers.get('User-Agent')
                    )
                
            except Exception as e:
                db.session.rollback()
                flash(f'Error al crear la incidencia: {str(e)}', 'error')

        return redirect(url_for('user.dashboard'))

    @staticmethod
    def update_incident(incident_id):
        if 'user_id' not in session:
            return redirect(url_for('auth.index'))

        incidencia = Incidencia.query.get(incident_id)
        if not incidencia or incidencia.usuario_creador_id != session['user_id']:
            flash('No tienes permiso para editar esta incidencia', 'error')
            return redirect(url_for('user.dashboard'))

        if request.method == 'POST':
            incidencia.titulo = request.form.get('titulo', incidencia.titulo)
            incidencia.descripcion = request.form.get('descripcion', incidencia.descripcion)
            incidencia.categoria_id = request.form.get('categoria_id', incidencia.categoria_id)
            incidencia.prioridad_id = request.form.get('prioridad_id', incidencia.prioridad_id)
            incidencia.fecha_ultima_actualizacion = datetime.utcnow()

            try:
                db.session.commit()
                flash('Incidencia actualizada exitosamente', 'success')
                log_action(
                    usuario_id=session['user_id'],
                     accion="actualizar",
                     entidad="incidencia",
                    entidad_id=incident_id,
                    detalles=f"Incidencia actualizada: '{incidencia.titulo}'",
                    user_agent=request.headers.get('User-Agent')
                    )


            except Exception as e:
                db.session.rollback()
                flash(f'Error al actualizar la incidencia: {str(e)}', 'error')

        return redirect(url_for('user.dashboard'))

    @staticmethod
    def delete_incident(incident_id):
        if 'user_id' not in session:
            return redirect(url_for('auth.index'))

        incidencia = Incidencia.query.get(incident_id)
        if not incidencia or incidencia.usuario_creador_id != session['user_id']:
            flash('No tienes permiso para eliminar esta incidencia', 'error')
            return redirect(url_for('user.dashboard'))

        try:
            # Eliminar comentarios asociados primero si es necesario
            Comentario.query.filter_by(incidencia_id=incident_id).delete()
            
            # Eliminar historial de estados
            HistorialEstado.query.filter_by(incidencia_id=incident_id).delete()
            
            # Finalmente eliminar la incidencia
            db.session.delete(incidencia)
            db.session.commit()
            flash('Incidencia eliminada exitosamente', 'success')
            log_action(
                usuario_id=session['user_id'],
                accion="eliminar",
                entidad="incidencia",
                entidad_id=incident_id,
                detalles=f"Incidencia '{incidencia.titulo}' eliminada",
                user_agent=request.headers.get('User-Agent')
                )

        except Exception as e:
            db.session.rollback()
            flash(f'Error al eliminar la incidencia: {str(e)}', 'error')

        return redirect(url_for('user.dashboard'))

    @staticmethod
    def view_incident(incident_id):
        if 'user_email' not in session:
            return redirect(url_for('auth.index'))

        usuario = Usuario.find_by_email(session['user_email'])
        if not usuario:
            return redirect(url_for('auth.index'))

        query = text("""
            SELECT 
                i.*,
                e.nombre AS estado_nombre,
                p.nombre AS prioridad_nombre,
                c.nombre AS categoria_nombre,
                u.nombre AS creador_nombre,
                u.apellido AS creador_apellido
            FROM incidencias i
            JOIN estados e ON i.estado_id = e.id
            JOIN prioridades p ON i.prioridad_id = p.id
            JOIN categorias c ON i.categoria_id = c.id
            JOIN usuarios u ON i.usuario_creador_id = u.id
            WHERE i.id = :incident_id
        """)

        incidencia = db.session.execute(query, {'incident_id': incident_id}).fetchone()

        if not incidencia or incidencia.usuario_creador_id != usuario.id:
            flash('No tienes permiso para ver esta incidencia', 'error')
            return redirect(url_for('user.dashboard'))

        comentarios = Comentario.get_by_incident(incident_id)

        # Verificar si el primer comentario tiene un usuario, y descifrar el nombre y apellido una sola vez
        if comentarios and comentarios[0].usuario:
            nombre_descifrado = decrypt(comentarios[0].usuario.nombre) if comentarios[0].usuario.nombre else None
            apellido_descifrado = decrypt(comentarios[0].usuario.apellido) if comentarios[0].usuario.apellido else None

            # Asignar el mismo nombre y apellido descifrado a todos los comentarios
            for comentario in comentarios:
                if comentario.usuario:
                    comentario.usuario.nombre = nombre_descifrado
                    comentario.usuario.apellido = apellido_descifrado


        # Obtener historial
        historial = db.session.execute(
            text("""
            SELECT h.*, 
                ea.nombre AS estado_anterior_nombre,
                en.nombre AS estado_nuevo_nombre,
                us.nombre AS usuario_nombre,
                us.apellido AS usuario_apellido
            FROM historial_estados h
            JOIN estados ea ON h.estado_anterior_id = ea.id
            JOIN estados en ON h.estado_nuevo_id = en.id
            JOIN usuarios us ON h.usuario_id = us.id
            WHERE h.incidencia_id = :incident_id
            ORDER BY h.fecha_cambio DESC
            """),
            {'incident_id': incident_id}
        ).fetchall()

        nombre = decrypt(usuario.nombre)
        apellido = decrypt(usuario.apellido)
        correo = session.get('user_email')

        return render_template('view_incident.html',
                            nombre=nombre,
                            apellido=apellido,
                            correo=correo,
                            incidencia=incidencia,
                            comentarios=comentarios,
                            historial=historial)

    @staticmethod
    def add_comment(incident_id):
        if 'user_id' not in session:
            return redirect(url_for('auth.index'))

        if request.method == 'POST':
            contenido = request.form.get('comment')
            if not contenido:
                flash('El comentario no puede estar vacío', 'error')
                return redirect(url_for('user.view_incident', incident_id=incident_id))

            incidencia = Incidencia.query.get(incident_id)
            if not incidencia or incidencia.usuario_creador_id != session['user_id']:
                flash('No tienes permiso para comentar esta incidencia', 'error')
                return redirect(url_for('user.dashboard'))

            comentario = Comentario(
                incidencia_id=incident_id,
                usuario_id=session['user_id'],
                contenido=contenido
            )

            db.session.add(comentario)
            try:
                db.session.commit()
                flash('Comentario añadido correctamente', 'success')
                log_action(
                    usuario_id=session['user_id'],
                    accion="comentar",
                    entidad="comentario",
                     entidad_id=comentario.id,
                    detalles=f"Comentario añadido en incidencia ID {incident_id}",
                    user_agent=request.headers.get('User-Agent')
                        )

            except Exception as e:
                db.session.rollback()
                flash(f'Error al añadir el comentario: {str(e)}', 'error')

        return redirect(url_for('user.view_incident', incident_id=incident_id))