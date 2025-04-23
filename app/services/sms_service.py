from twilio.rest import Client
from flask import current_app

def send_sms(to_number, message):
    """
    Envía un mensaje SMS usando la API de Twilio

    Args:
        to_number (str): Número de teléfono del destinatario
        message (str): Contenido del mensaje
    """
    try:
        if not to_number or not message:
            raise ValueError("Los campos 'to_number' y 'message' no pueden estar vacíos")

        account_sid = current_app.config.get('TWILIO_ACCOUNT_SID')
        auth_token = current_app.config.get('TWILIO_AUTH_TOKEN')
        from_number = current_app.config.get('TWILIO_PHONE_NUMBER')

        if not all([account_sid, auth_token, from_number]):
            raise ValueError("Faltan credenciales de Twilio en la configuración")

        client = Client(account_sid, auth_token)

        message = client.messages.create(
            body=message,
            from_=from_number,
            to=to_number
        )

        return True
    except Exception as e:
        current_app.logger.error(f"Error al enviar SMS: {str(e)}")
        return False