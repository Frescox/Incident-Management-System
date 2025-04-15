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
        account_sid = current_app.config['TWILIO_ACCOUNT_SID']
        auth_token = current_app.config['TWILIO_AUTH_TOKEN']
        from_number = current_app.config['TWILIO_PHONE_NUMBER']
        
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