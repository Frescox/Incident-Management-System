from flask import render_template, session, redirect, url_for, flash
from app.models.ticket_models import Incidencia
from app.models.catalog_models import Estado, Prioridad, Categoria
from app.models import db
from app.models.user import Usuario
from app.utils.aes_encryption import decrypt
from sqlalchemy import text

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
            incidencias.append(incidencia)

        return render_template('admin_dashboard.html',
                               nombre=nombre,
                               apellido=apellido,
                               correo=correo,
                               incidencias=incidencias)

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

        comentarios = db.session.execute(text("""
            SELECT co.*, us.nombre AS usuario_nombre, us.apellido AS usuario_apellido
            FROM comentarios co
            JOIN usuarios us ON co.usuario_id = us.id
            WHERE co.incidencia_id = :incident_id
            ORDER BY co.fecha_creacion ASC
        """), {'incident_id': incident_id}).fetchall()

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
