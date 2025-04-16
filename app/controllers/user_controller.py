from flask import render_template, session, redirect, url_for, request, flash, jsonify
from app.models.user import Usuario
from app.models.ticket_models import Incidencia, Comentario, HistorialEstado
from app.models.catalog_models import Estado, Prioridad, Categoria
from app.utils.aes_encryption import decrypt
from datetime import datetime
from app.models import db  # Importa el SQLAlchemy db

class UserController:
    @staticmethod
    def dashboard():
        if 'user_email' not in session:
            return redirect(url_for('auth.index'))

        usuario = Usuario.find_by_email(session['user_email'])
        if not usuario:
            return redirect(url_for('auth.index'))

        nombre = decrypt(usuario.nombre)
        apellido = decrypt(usuario.apellido)
        correo = session.get('user_email')
        
        # Get user's incidents with related data
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

            nueva_incidencia = Incidencia(
                titulo=titulo,
                descripcion=descripcion,
                categoria_id=categoria_id,
                prioridad_id=prioridad_id,
                estado_id=1,  # Estado "nuevo"
                usuario_creador_id=session['user_id'],
                fecha_creacion=datetime.utcnow(),
                fecha_ultima_actualizacion=datetime.utcnow()
            )

            db.session.add(nueva_incidencia)
            try:
                db.session.commit()
                flash('Incidencia creada exitosamente', 'success')
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

        # Get incident with all related data
        incidencia = db.session.query(Incidencia).filter_by(
            id=incident_id
        ).join(
            Estado, Incidencia.estado_id == Estado.id
        ).join(
            Prioridad, Incidencia.prioridad_id == Prioridad.id
        ).join(
            Categoria, Incidencia.categoria_id == Categoria.id
        ).join(
            Usuario, Incidencia.usuario_creador_id == Usuario.id
        ).add_columns(
            Incidencia.id,
            Incidencia.titulo,
            Incidencia.descripcion,
            Incidencia.fecha_creacion,
            Incidencia.fecha_ultima_actualizacion,
            Estado.nombre.label('estado_nombre'),
            Prioridad.nombre.label('prioridad_nombre'),
            Categoria.nombre.label('categoria_nombre'),
            Usuario.nombre.label('creador_nombre'),
            Usuario.apellido.label('creador_apellido')
        ).first()

        if not incidencia or incidencia.usuario_creador_id != usuario.id:
            flash('No tienes permiso para ver esta incidencia', 'error')
            return redirect(url_for('user.dashboard'))

        # Get comments with user data
        comentarios = db.session.query(Comentario).filter_by(
            incidencia_id=incident_id
        ).join(
            Usuario, Comentario.usuario_id == Usuario.id
        ).add_columns(
            Comentario.id,
            Comentario.contenido,
            Comentario.fecha_creacion,
            Usuario.nombre.label('usuario_nombre'),
            Usuario.apellido.label('usuario_apellido')
        ).order_by(
            Comentario.fecha_creacion.asc()
        ).all()

        # Get status history
        historial = db.session.query(HistorialEstado).filter_by(
            incidencia_id=incident_id
        ).join(
            Estado, HistorialEstado.estado_anterior_id == Estado.id
        ).join(
            Estado, HistorialEstado.estado_nuevo_id == Estado.id
        ).join(
            Usuario, HistorialEstado.usuario_id == Usuario.id
        ).add_columns(
            HistorialEstado.id,
            HistorialEstado.comentario,
            HistorialEstado.fecha_cambio,
            Estado.nombre.label('estado_anterior'),
            Estado.nombre.label('estado_nuevo'),
            Usuario.nombre.label('usuario_nombre'),
            Usuario.apellido.label('usuario_apellido')
        ).order_by(
            HistorialEstado.fecha_cambio.desc()
        ).all()

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
            except Exception as e:
                db.session.rollback()
                flash(f'Error al añadir el comentario: {str(e)}', 'error')

        return redirect(url_for('user.view_incident', incident_id=incident_id))