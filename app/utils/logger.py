from datetime import datetime
from app.models import db

def log_action(usuario_id, accion, entidad, entidad_id, detalles=None, user_agent=None):
    """
    Inserta un registro de actividad en la tabla log_actividad usando SQLAlchemy ORM.

    Args:
        usuario_id (int): ID del usuario que realiza la acción.
        accion (str): Acción realizada (crear, actualizar, etc).
        entidad (str): Entidad afectada (incidencia, comentario, etc).
        entidad_id (int): ID de la entidad.
        detalles (str, opcional): Descripción adicional.
        user_agent (str, opcional): Agente del navegador (para contexto).
    """
    try:
        sql = """
            INSERT INTO log_actividad (usuario_id, accion, entidad, entidad_id, detalles, user_agent, created_at)
            VALUES (:usuario_id, :accion, :entidad, :entidad_id, :detalles, :user_agent, :created_at)
        """
        db.session.execute(
            db.text(sql),
            {
                'usuario_id': usuario_id,
                'accion': accion,
                'entidad': entidad,
                'entidad_id': entidad_id,
                'detalles': detalles,
                'user_agent': user_agent,
                'created_at': datetime.now()
            }
        )
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f"[ERROR] No se pudo registrar el log de actividad: {e}")