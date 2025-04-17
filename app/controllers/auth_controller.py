from flask import request, render_template, redirect, url_for, session, flash, jsonify
from app.models.user import Usuario
from app.models.ticket_models import Incidencia, Comentario, HistorialEstado
from app.models.catalog_models import Estado, Prioridad, Categoria
from app.services.mail_service import send_email
from app.services.sms_service import send_sms
from app.utils.aes_encryption import encrypt, decrypt

class AuthController:
    @staticmethod
    def index():
        return render_template('index.html')
    

    # Funcion para registrar un nuevo usuario
    @staticmethod
    def register():
        if request.method == 'POST':
            try:
                nombre = request.form.get('nombre')
                apellido = request.form.get('apellido')
                email = request.form.get('email')
                password = request.form.get('password')
                telefono = request.form.get('telefono')
                metodo_verificacion = request.form.get('metodo_verificacion')

                if not all([nombre, apellido, email, password, metodo_verificacion]):
                    return jsonify({
                        'success': False,
                        'message': 'Todos los campos son obligatorios'
                    })

                if metodo_verificacion == 'sms' and not telefono:
                    return jsonify({
                        'success': False,
                        'message': 'El número de teléfono es requerido para verificación por SMS'
                    })

                usuario_existente = Usuario.find_by_email(email)
                if usuario_existente:
                    return jsonify({
                        'success': False,
                        'message': 'El correo electrónico ya está registrado'
                    })

                nombre_encriptado = encrypt(nombre)
                apellido_encriptado = encrypt(apellido)
                email_encriptado = encrypt(email)
                password_encriptado = encrypt(password)
                telefono_encriptado = encrypt(telefono) if telefono else None

                nuevo_usuario = Usuario(
                    nombre=nombre_encriptado,
                    apellido=apellido_encriptado,
                    email=email_encriptado,
                    password=password_encriptado,
                    telefono=telefono_encriptado,
                    metodo_verificacion=metodo_verificacion,
                    verificado=False
                )

                otp = nuevo_usuario.generate_otp()

                if metodo_verificacion == 'email':
                    subject = 'Verificación de cuenta - Sistema de Gestión de Incidencias'
                    body = f'Tu código de verificación es: {otp}. Es válido por 15 minutos.'
                    send_email(email, subject, body)
                elif metodo_verificacion == 'sms':
                    message = f'Tu código de verificación para el Sistema de Gestión de Incidencias es: {otp}'
                    send_sms(telefono, message)

                nuevo_usuario.save()
                session['user_email'] = email

                return jsonify({
                    'success': True,
                    'message': f'Te hemos enviado un código de verificación a tu {metodo_verificacion}',
                    'show_otp_verification': True
                })

            except Exception as e:
                return jsonify({'success': False, 'message': str(e)})

        return jsonify({'success': False, 'message': 'Método no permitido'})
    

    # Funcion para verificar el codigo enviado por el metodo de autentificacion elegido
    @staticmethod
    def verify_otp():
        if request.method == 'POST':
            try:
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
                    session['user_id'] = usuario.id
                    session['user_email'] = email
                    session['user_role'] = usuario.rol_id

                    if session['user_role'] == 1:
                        redirect_endpoint = 'auth.index'
                    elif session['user_role'] == 2:
                        redirect_endpoint = 'auth.index'
                    elif session['user_role'] == 3:
                        redirect_endpoint = 'auth.index'
                    else:
                        return jsonify({'success': False, 'message': 'Rol desconocido'})

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

            except Exception as e:
                return jsonify({'success': False, 'message': str(e)})

        return jsonify({'success': False, 'message': 'Método no permitido'})

    # Funcion para iniciar sesion
    @staticmethod
    def login():
        if request.method == 'POST':
            try:
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

                password_desencriptado = decrypt(usuario.password)
                if password != password_desencriptado:
                    return jsonify({
                        'success': False,
                        'message': 'Credenciales inválidas'
                    })

                if not usuario.verificado:
                    otp = usuario.generate_otp()

                    if usuario.metodo_verificacion == 'email':
                        subject = 'Verificación de cuenta - Sistema de Gestión de Incidencias'
                        body = f'Tu código de verificación es: {otp}. Es válido por 15 minutos.'
                        send_email(email, subject, body)
                    elif usuario.metodo_verificacion == 'sms':
                        telefono_desencriptado = decrypt(usuario.telefono) if usuario.telefono else None
                        print(f"Usuario.telefono: {usuario.telefono}")
                        send_sms(telefono_desencriptado, f'Tu código de verificación para el Sistema de Gestión de Incidencias es: {otp}')

                    session['user_email'] = email

                    return jsonify({
                        'success': True,
                        'message': f'Tu cuenta aún no está verificada. Te hemos enviado un nuevo código a tu {usuario.metodo_verificacion}',
                        'show_otp_verification': True
                    })

                session['user_id'] = usuario.id
                session['user_email'] = email
                session['user_role'] = usuario.rol_id

                if session['user_role'] == 1:
                    redirect_endpoint = 'agent.dashboard'
                elif session['user_role'] == 2:
                    redirect_endpoint = 'agent.dashboard'
                elif session['user_role'] == 3:
                    redirect_endpoint = 'user.dashboard'
                else:
                    return jsonify({'success': False, 'message': 'Rol desconocido'})

                usuario.update_login_timestamp()

                return jsonify({
                    'success': True,
                    'message': 'Inicio de sesión exitoso',
                    'redirect': url_for(redirect_endpoint)
                })

            except Exception as e:
                return jsonify({'success': False, 'message': str(e)})

        return jsonify({'success': False, 'message': 'Método no permitido'})

    @staticmethod
    def logout():
        session.clear()
        return redirect(url_for('auth.index'))
