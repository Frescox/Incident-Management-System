from flask import render_template, session, redirect, url_for, flash, request
from app.models.ticket_models import Incidencia, Comentario, HistorialEstado
from app.models.catalog_models import Estado, Prioridad, Categoria
from app.models import db
from app.models.user import Usuario
from app.utils.aes_encryption import decrypt    
from sqlalchemy import text

def get_decrypted_user_name(user_id):
    result = db.session.execute(text("SELECT nombre, apellido FROM usuarios WHERE id = :id"), {'id': user_id}).fetchone()
    if result:
        try:
            nombre = decrypt(result.nombre)
            apellido = decrypt(result.apellido)
            return f"{nombre} {apellido}"
        except Exception:
            return f"Usuario {user_id}"
    return f"Usuario {user_id}"

def safe_decrypt(value):
    try:
        return decrypt(value)
    except Exception:
        return value

class AdminController:
    @staticmethod
    def dashboard():
        if 'user_email' not in session:
            return redirect(url_for('auth.index'))

        usuario = Usuario.find_by_email(session['user_email'])
        if not usuario or usuario.rol_id != 1:
            return redirect(url_for('auth.index'))

        nombre = decrypt(usuario.nombre)
        apellido = decrypt(usuario.apellido)
        correo = session.get('user_email')

        # Obtener todas las incidencias
        resultados_raw = db.session.execute(text("""
            SELECT i.id, i.titulo, i.descripcion, i.fecha_creacion,
                   e.nombre AS estado_nombre,
                   p.nombre AS prioridad_nombre,
                   c.nombre AS categoria_nombre,
                   uc.nombre AS creador_nombre, uc.apellido AS creador_apellido,
                   ua.nombre AS agente_nombre, ua.apellido AS agente_apellido
            FROM incidencias i
            JOIN estados e ON i.estado_id = e.id
            JOIN prioridades p ON i.prioridad_id = p.id
            JOIN categorias c ON i.categoria_id = c.id
            JOIN usuarios uc ON i.usuario_creador_id = uc.id
            LEFT JOIN usuarios ua ON i.agente_asignado_id = ua.id
            ORDER BY i.fecha_creacion DESC
        """)).fetchall()

        incidencias = []
        for row in resultados_raw:
            incidencia = dict(row._mapping)
            incidencia["creador_nombre"] = safe_decrypt(incidencia.get("creador_nombre"))
            incidencia["creador_apellido"] = safe_decrypt(incidencia.get("creador_apellido"))
            agente_nombre = incidencia.get("agente_nombre")
            agente_apellido = incidencia.get("agente_apellido")
            incidencia["agente_nombre"] = safe_decrypt(agente_nombre) if agente_nombre else "Sin agente"
            incidencia["agente_apellido"] = safe_decrypt(agente_apellido) if agente_apellido else ""

            # Obtener logs relacionados con esta incidencia
            logs_raw = db.session.execute(text("""
                SELECT * FROM log_actividad
                WHERE entidad = 'incidencia' AND entidad_id = :incidencia_id
                ORDER BY created_at DESC
            """), {'incidencia_id': incidencia['id']}).fetchall()

            # Convertir a lista de diccionarios
            logs = []
            for log in logs_raw:
                log_dict = dict(log._mapping)
                log_dict['usuario_nombre'] = get_decrypted_user_name(log_dict['usuario_id'])
                logs.append(log_dict)


            incidencia['logs'] = logs

            incidencias.append(incidencia)
            
        # Obtener todos los usuarios
        usuarios_raw = db.session.execute(text("""
            SELECT u.id, u.nombre, u.apellido, u.email, u.estado, 
                   r.nombre AS rol_nombre, r.id AS rol_id
            FROM usuarios u
            JOIN roles r ON u.rol_id = r.id
            ORDER BY u.id
        """)).fetchall()

        usuarios = []
        for row in usuarios_raw:
            usuario = dict(row._mapping)
            usuario["nombre"] = safe_decrypt(usuario.get("nombre"))
            usuario["apellido"] = safe_decrypt(usuario.get("apellido"))
            usuario["email"] = safe_decrypt(usuario.get("email"))
    
             # Obtener logs para cada usuario individualmente
            logs_raw = db.session.execute(text("""
                SELECT la.*, u.nombre, u.apellido
                FROM log_actividad la
                JOIN usuarios u ON la.usuario_id = u.id
                WHERE la.usuario_id = :user_id
                ORDER BY la.created_at DESC
            """), {'user_id': usuario['id']}).fetchall()

            logs = []
            for log in logs_raw:
                logs.append({
                    'usuario_nombre': f"{safe_decrypt(log.nombre)} {safe_decrypt(log.apellido)}",
                    'accion': log.accion,
                    'entidad': log.entidad,
                    'entidad_id': log.entidad_id,
                    'detalles': log.detalles,
                    'created_at': log.created_at
                })

            usuario['logs'] = logs
            usuarios.append(usuario)


        # Obtener todos los roles disponibles
        roles = db.session.execute(text("SELECT * FROM roles")).fetchall()

        return render_template('admin_dashboard.html',
                           nombre=nombre,
                           apellido=apellido,
                           correo=correo,
                           incidencias=incidencias,
                           usuarios=usuarios,
                           roles=roles)

    @staticmethod
    def view_incident(incident_id):
        if 'user_email' not in session:
            return redirect(url_for('auth.index'))

        usuario = Usuario.find_by_email(session['user_email'])
        if not usuario or usuario.rol_id != 1:
            return redirect(url_for('auth.index'))

        query = db.session.execute(text("""
            SELECT i.*, e.nombre AS estado_nombre, p.nombre AS prioridad_nombre,
                   c.nombre AS categoria_nombre, uc.nombre AS creador_nombre, uc.apellido AS creador_apellido,
                   ua.nombre AS agente_nombre, ua.apellido AS agente_apellido
            FROM incidencias i
            JOIN estados e ON i.estado_id = e.id
            JOIN prioridades p ON i.prioridad_id = p.id
            JOIN categorias c ON i.categoria_id = c.id
            JOIN usuarios uc ON i.usuario_creador_id = uc.id
            LEFT JOIN usuarios ua ON i.agente_asignado_id = ua.id
            WHERE i.id = :incident_id
        """), {'incident_id': incident_id}).fetchone()

        if not query:
            flash('Incidencia no encontrada', 'error')
            return redirect(url_for('admin.dashboard'))

        incidencia = dict(query._mapping)
        incidencia["creador_nombre"] = safe_decrypt(incidencia.get("creador_nombre"))
        incidencia["creador_apellido"] = safe_decrypt(incidencia.get("creador_apellido"))
        agente_nombre = incidencia.get("agente_nombre")
        agente_apellido = incidencia.get("agente_apellido")
        incidencia["agente_nombre"] = safe_decrypt(agente_nombre) if agente_nombre else "Sin agente"
        incidencia["agente_apellido"] = safe_decrypt(agente_apellido) if agente_apellido else ""

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

        historial = db.session.execute(text("""
            SELECT h.*, ea.nombre AS estado_anterior_nombre, en.nombre AS estado_nuevo_nombre,
                   us.nombre AS usuario_nombre, us.apellido AS usuario_apellido
            FROM historial_estados h
            JOIN estados ea ON h.estado_anterior_id = ea.id
            JOIN estados en ON h.estado_nuevo_id = en.id
            JOIN usuarios us ON h.usuario_id = us.id
            WHERE h.incidencia_id = :incident_id
            ORDER BY h.fecha_cambio DESC
        """), {'incident_id': incident_id}).fetchall()

        nombre = decrypt(usuario.nombre)
        apellido = decrypt(usuario.apellido)
        correo = session.get('user_email')

        return render_template('admin_view_incident.html',
                           nombre=nombre,
                           apellido=apellido,
                           correo=correo,
                           incidencia=incidencia,
                           comentarios=comentarios,
                           historial=historial)

    @staticmethod
    def update_user_role(user_id):
        if 'user_email' not in session:
            return redirect(url_for('auth.index'))

        usuario = Usuario.find_by_email(session['user_email'])
        if not usuario or usuario.rol_id != 1:
            return redirect(url_for('auth.index'))

        if request.method == 'POST':
            nuevo_rol_id = request.form.get('rol_id')
            
            # Verificar que no se está modificando a sí mismo
            if usuario.id == user_id:
                flash('No puedes cambiar tu propio rol', 'error')
                return redirect(url_for('admin.dashboard'))
            
            # Actualizar el rol del usuario
            db.session.execute(text("""
                UPDATE usuarios SET rol_id = :rol_id WHERE id = :user_id
            """), {'rol_id': nuevo_rol_id, 'user_id': user_id})
            
            try:
                db.session.commit()
                flash('Rol actualizado correctamente', 'success')
            except Exception as e:
                db.session.rollback()
                flash(f'Error al actualizar el rol: {str(e)}', 'error')

        return redirect(url_for('admin.dashboard'))

    @staticmethod
    def toggle_user_status(user_id):
        if 'user_email' not in session:
            return redirect(url_for('auth.index'))

        usuario = Usuario.find_by_email(session['user_email'])
        if not usuario or usuario.rol_id != 1:
            return redirect(url_for('auth.index'))

        # Verificar que no se está desactivando a sí mismo
        if usuario.id == user_id:
            flash('No puedes cambiar tu propio estado', 'error')
            return redirect(url_for('admin.dashboard'))

        # Obtener el usuario a modificar
        user_to_toggle = Usuario.find_by_id(user_id)
        if not user_to_toggle:
            flash('Usuario no encontrado', 'error')
            return redirect(url_for('admin.dashboard'))

        # Cambiar el estado del usuario (toggle)
        new_status = not user_to_toggle.estado
        
        try:
            db.session.execute(text("""
                UPDATE usuarios SET estado = :estado WHERE id = :user_id
            """), {'estado': new_status, 'user_id': user_id})
            db.session.commit()
            
            status_msg = "desactivado" if not new_status else "activado"
            flash(f'Usuario {status_msg} correctamente', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error al actualizar estado: {str(e)}', 'error')

        return redirect(url_for('admin.dashboard'))
    
    @staticmethod
    def view_logs():
        if 'user_email' not in session:
            return redirect(url_for('auth.index'))

        usuario = Usuario.find_by_email(session['user_email'])
        if not usuario or usuario.rol_id != 1:
            return redirect(url_for('auth.index'))

        nombre = decrypt(usuario.nombre)
        apellido = decrypt(usuario.apellido)
        correo = session.get('user_email')

        resultado = db.session.execute(text("""
            SELECT l.usuario_id, u.nombre, u.apellido, l.accion, l.entidad, 
                   l.entidad_id, l.detalles, l.created_at
            FROM log_actividad l
            JOIN usuarios u ON l.usuario_id = u.id
            ORDER BY l.created_at DESC
        """)).fetchall()

        logs = []
        for row in resultado:
            r = dict(row._mapping)
            r["nombre"] = safe_decrypt(r["nombre"])
            r["apellido"] = safe_decrypt(r["apellido"])
            logs.append(r)

        return render_template("admin_logs.html",
                               nombre=nombre,
                               apellido=apellido,
                               correo=correo,
                               logs=logs)
    
    @staticmethod
    def logs_by_incident(incident_id):
        if 'user_email' not in session:
            return redirect(url_for('auth.index'))
        
        usuario = Usuario.find_by_email(session['user_email'])
        if not usuario or usuario.rol_id != 1:
            return redirect(url_for('auth.index'))

        logs = db.session.execute(text("""
            SELECT la.*, u.nombre, u.apellido
            FROM log_actividad la
            JOIN usuarios u ON la.usuario_id = u.id
            WHERE la.entidad = 'incidencia' AND la.entidad_id = :incident_id
            ORDER BY la.created_at DESC
        """), {'incident_id': incident_id}).fetchall()

        return render_template("admin_logs.html", logs=logs, titulo=f"Logs de la incidencia #{incident_id}")

    @staticmethod
    def logs_by_user(user_id):
        if 'user_email' not in session:
            return redirect(url_for('auth.index'))
        
        usuario = Usuario.find_by_email(session['user_email'])
        if not usuario or usuario.rol_id != 1:
            return redirect(url_for('auth.index'))

        resultados = db.session.execute(text("""
            SELECT la.*, u.nombre, u.apellido
            FROM log_actividad la
            JOIN usuarios u ON la.usuario_id = u.id
            WHERE la.usuario_id = :user_id
            ORDER BY la.created_at DESC
        """), {'user_id': user_id}).fetchall()

        logs = []
        for row in resultados:
            nombre = safe_decrypt(row.nombre)
            apellido = safe_decrypt(row.apellido)
            logs.append({
                'usuario_nombre': f"{nombre} {apellido}",
                'accion': row.accion,
                'entidad': row.entidad,
                'entidad_id': row.entidad_id,
                'detalles': row.detalles,
                'created_at': row.created_at
            })

        return render_template("admin_logs.html", logs=logs, titulo=f"Logs del usuario ID #{user_id}")
