from flask_mail import Mail, Message
from flask import current_app

mail = Mail()

def init_mail(app):
    mail.init_app(app)

def send_email(to, subject, body):
    """
    Envía un correo electrónico
    
    Args:
        to (str): Dirección de correo electrónico del destinatario
        subject (str): Asunto del correo
        body (str): Contenido del correo
    """
    try:
        msg = Message(
            subject=subject,
            recipients=[to],
            body=body,
            sender=current_app.config['MAIL_DEFAULT_SENDER']
        )
        mail.send(msg)
        return True
    except Exception as e:
        current_app.logger.error(f"Error al enviar correo: {str(e)}")
        return False