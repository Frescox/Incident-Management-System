from flask import current_app
from app.services.mail_service import send_email
from app.db.database import db
from app.utils.aes_encryption import decrypt

class NotificationService:
    def __init__(self):
        self.db = db

    def get_user_email_by_incident(self, incidencia_id):
        """
        Obtiene el correo del usuario que reportó la incidencia.
        """
        if not incidencia_id:
            raise ValueError("incidencia_id no puede estar vacío")

        query = """
        SELECT u.email
        FROM incidencias i
        JOIN usuarios u ON i.usuario_creador_id = u.id
        WHERE i.id = %s
        """
        result = self.db.execute_query(query, (incidencia_id,))
        if not result or not result[0].get("email"):
            raise ValueError("No se pudo encontrar el correo del usuario")
       
        # Desencriptar el correo
        try:
            email_desencriptado = decrypt(result[0]["email"])
            return email_desencriptado
        except Exception as e:
            current_app.logger.error(f"Error al desencriptar el correo: {str(e)}")
            raise ValueError("Error al desencriptar el correo del usuario")


    def notify_status_change(self, incidencia_id, nuevo_estado, comentario):
        """
        Envía un correo cuando cambia el estado de la incidencia.
        """
        if not nuevo_estado:
            raise ValueError("nuevo_estado no puede estar vacío")

        try:
            correo = self.get_user_email_by_incident(incidencia_id)
            asunto = f"Actualización de su incidencia #{incidencia_id}"
            cuerpo = f"Hola,\n\nEl estado de su incidencia ha cambiado a: {nuevo_estado}.\n\n{comentario}\n\nGracias por usar nuestro sistema."

            enviado = send_email(correo, asunto, cuerpo)
            if not enviado:
                current_app.logger.warning(f"No se pudo enviar notificación a {correo}")
            return enviado
        except Exception as e:
            current_app.logger.error(f"Error al enviar notificación: {str(e)}")
            return False
