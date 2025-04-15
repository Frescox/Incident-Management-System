from flask import request, render_template, redirect, url_for, session, flash, jsonify
from app.models.user import Usuario
from app.services.mail_service import send_email
from app.services.sms_service import send_sms
from app.utils.aes_encryption import encrypt, decrypt  # Importando las funciones de encriptación
import random
import time

class AuthController:
    @staticmethod
    def index():
        return render_template('index.html')
    
    @staticmethod
    def register():
        if request.method == 'POST':
            # Obtener datos del formulario
            nombre = request.form.get('nombre')
            apellido = request.form.get('apellido')
            email = request.form.get('email')
            password = request.form.get('password')
            telefono = request.form.get('telefono')
            metodo_verificacion = request.form.get('metodo_verificacion')
            
            # Validar datos
            if not all([nombre, apellido, email, password, metodo_verificacion]):
                return jsonify({
                    'success': False,
                    'message': 'Todos los campos son obligatorios'
                })
                
            # Verificar si el método de verificación es SMS pero no hay teléfono
            if metodo_verificacion == 'sms' and not telefono:
                return jsonify({
                    'success': False,
                    'message': 'El número de teléfono es requerido para verificación por SMS'
                })
            
            # Verificar si el usuario ya existe
            # Aquí buscamos por el email no encriptado primero
            usuario_existente = Usuario.find_by_email(email)
            if usuario_existente:
                return jsonify({
                    'success': False,
                    'message': 'El correo electrónico ya está registrado'
                })
            
            # Encriptar los datos sensibles
            nombre_encriptado = encrypt(nombre)
            apellido_encriptado = encrypt(apellido)
            email_encriptado = encrypt(email)  # Encriptamos el email para almacenamiento
            password_encriptado = encrypt(password)
            telefono_encriptado = encrypt(telefono) if telefono else None
            
            # Crear nuevo usuario con datos encriptados
            nuevo_usuario = Usuario(
                nombre=nombre_encriptado,
                apellido=apellido_encriptado,
                email=email_encriptado, 
                password=password_encriptado,
                telefono=telefono_encriptado,
                metodo_verificacion=metodo_verificacion,
                verificado=False
            )
            
            # Generar OTP
            otp = nuevo_usuario.generate_otp()
            
            # Enviar OTP según el método seleccionado
            if metodo_verificacion == 'email':
                subject = 'Verificación de cuenta - Sistema de Gestión de Incidencias'
                body = f'Tu código de verificación es: {otp}. Es válido por 15 minutos.'
                send_email(email, subject, body)  # Usar email sin encriptar para envío
            elif metodo_verificacion == 'sms':
                message = f'Tu código de verificación para el Sistema de Gestión de Incidencias es: {otp}'
                send_sms(telefono, message)  # Usar teléfono sin encriptar para envío
            
            # Guardar usuario en la base de datos
            nuevo_usuario.save()
            
            # Guardar información en la sesión para la verificación
            session['user_email'] = email  # Guardar email sin encriptar en la sesión
            
            return jsonify({
                'success': True,
                'message': f'Te hemos enviado un código de verificación a tu {metodo_verificacion}',
                'show_otp_verification': True
            })
            
        # Si no es POST, devolver error
        return jsonify({'success': False, 'message': 'Método no permitido'})
    
    @staticmethod
    def verify_otp():
        if request.method == 'POST':
            email = session.get('user_email')
            otp = request.form.get('otp')
            
            if not email or not otp:
                return jsonify({
                    'success': False,
                    'message': 'Información incompleta'
                })
            
            usuario = Usuario.find_by_email(email)
            if not usuario:
                return jsonify({
                    'success': False,
                    'message': 'Usuario No Encontrado'
                })
            
            if usuario.verify_otp(otp):
                # Iniciar sesión del usuario
                session['user_id'] = usuario.id
                session['user_email'] = email  # Email sin encriptar para uso en sesión
                session['user_role'] = usuario.rol_id

                if session['user_role'] == 1:
                    redirect_endpoint = 'agent.dashboard'
                elif session['user_role'] == 2:
                    redirect_endpoint = 'agent.dashboard'
                elif session['user_role'] == 3:
                    redirect_endpoint = 'user.dashboard'

                return jsonify({
                    'success': True,
                    'message': 'Verificación exitosa, redirigiendo...',
                    'redirect': url_for(redirect_endpoint)
                })
            else:
                return jsonify({
                    'success': False,
                    'message': 'Código inválido o expirado'
                })
                
        return jsonify({'success': False, 'message': 'Método no permitido'})
    
    @staticmethod
    def login():
        if request.method == 'POST':
            email = request.form.get('email')
            password = request.form.get('password')
            
            if not all([email, password]):
                return jsonify({
                    'success': False,
                    'message': 'Email y contraseña son requeridos'
                })
                
            usuario = Usuario.find_by_email(email)
            
            if not usuario:
                return jsonify({
                    'success': False,
                    'message': 'Credenciales inválidas'
                })
            
            # Desencriptar la contraseña almacenada y comparar con la proporcionada
            password_desencriptado = decrypt(usuario.password)
            
            if password != password_desencriptado:
                return jsonify({
                    'success': False,
                    'message': 'Credenciales inválidas'
                })
                
            if not usuario.verificado:
                # Si el usuario no está verificado, generar nuevo OTP
                otp = usuario.generate_otp()
                
                if usuario.metodo_verificacion == 'email':
                    subject = 'Verificación de cuenta - Sistema de Gestión de Incidencias'
                    body = f'Tu código de verificación es: {otp}. Es válido por 15 minutos.'
                    send_email(email, subject, body)  # Email sin encriptar para envío
                elif usuario.metodo_verificacion == 'sms':
                    message = f'Tu código de verificación para el Sistema de Gestión de Incidencias es: {otp}'
                    telefono_desencriptado = decrypt(usuario.telefono) if usuario.telefono else None
                    send_sms(telefono_desencriptado, message)  # Teléfono desencriptado para envío
                
                session['user_email'] = email
                
                return jsonify({
                    'success': True,
                    'message': f'Tu cuenta aún no está verificada. Te hemos enviado un nuevo código a tu {usuario.metodo_verificacion}',
                    'show_otp_verification': True
                })
            
            # Iniciar sesión
            session['user_id'] = usuario.id
            session['user_email'] = email  # Email sin encriptar para uso en sesión
            session['user_role'] = usuario.rol_id

            if session['user_role'] == 1:
                redirect_endpoint = 'agent.dashboard'
            elif session['user_role'] == 2:
                redirect_endpoint = 'agent.dashboard'
            elif session['user_role'] == 3:
                redirect_endpoint = 'user.dashboard'

            # Actualizar último login
            usuario.update_login_timestamp()
            
            return jsonify({
                'success': True,
                'message': 'Inicio de sesión exitoso',
                'redirect': url_for(redirect_endpoint)
            })
            
        return jsonify({'success': False, 'message': 'Método no permitido'})
    
    @staticmethod
    def logout():
        session.clear()
        return redirect(url_for('auth.index'))
