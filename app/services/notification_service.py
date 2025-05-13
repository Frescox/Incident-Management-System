from flask import current_app
from app.services.mail_service import send_email
from app.utils.aes_encryption import decrypt
from app.models.core import db
from app.models.ticket_models import Incidencia


class NotificationService:
    def __init__(self):
        self.db = db

    def get_user_email_by_incident(self, incidencia_id):
        if not incidencia_id:
            raise ValueError("incidencia_id no puede estar vacío")

        incidencia = self.db.session.query(Incidencia).filter_by(id=incidencia_id).first()

        if not incidencia or not incidencia.creador or not incidencia.creador.email:
            raise ValueError("No se pudo encontrar el correo del usuario")

        try:
            email_desencriptado = decrypt(incidencia.creador.email)
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