from flask_mail import Mail, Message
from flask import current_app

mail = Mail()

def init_mail(app):
    try:
        mail.init_app(app)
    except Exception as e:
        current_app.logger.error(f"Error al inicializar Mail: {str(e)}")

def send_email(to, subject, body):
    """
    Envía un correo electrónico

    Args:
        to (str): Dirección de correo electrónico del destinatario
        subject (str): Asunto del correo
        body (str): Contenido del correo
    """
    try:
        if not to or not subject or not body:
            raise ValueError("Los campos 'to', 'subject' y 'body' no pueden estar vacíos")

        sender = current_app.config.get('MAIL_DEFAULT_SENDER')
        if not sender:
            raise ValueError("MAIL_DEFAULT_SENDER no está configurado")

        msg = Message(
            subject=subject,
            recipients=[to],
            body=body,
            sender=sender
        )
        mail.send(msg)
        return True
    except Exception as e:
        current_app.logger.error(f"Error al enviar correo: {str(e)}")
        return False