from flask import request, jsonify, session, redirect, url_for, render_template
from app.models.user_rol_models import Usuario
from app.services.mail_service import send_email
from app.services.sms_service import send_sms
from app.utils.aes_encryption import encrypt, decrypt

class AuthController:
    @staticmethod
    def index():
        """Renderiza la página principal de autenticación"""
        return render_template('index.html')

    @staticmethod
    def register():
        if request.method == 'GET':
            # Lógica para mostrar el formulario de login
            return render_template('index.html')
        
        if request.method == 'POST':
            try:
                data = request.get_json() if request.is_json else request.form
                nombre = data.get('nombre')
                apellido = data.get('apellido')
                email = data.get('email')
                password = data.get('password')
                telefono = data.get('telefono')
                metodo_verificacion = data.get('metodo_verificacion')

                if not all([nombre, apellido, email, password, metodo_verificacion]):
                    return jsonify({'success': False, 'message': 'Todos los campos son obligatorios'}), 400

                # Verificar si el email ya existe (con desencriptación)
                existing_user = Usuario.find_by_email(email)
                if existing_user:
                    return jsonify({'success': False, 'message': 'El correo ya está registrado'}), 400

                # Crear nuevo usuario (todo encriptado)
                nuevo_usuario = Usuario(
                    nombre=encrypt(nombre),
                    apellido=encrypt(apellido),
                    email=encrypt(email),  # El email se encripta
                    password=encrypt(password),
                    telefono=encrypt(telefono) if telefono else None,
                    metodo_verificacion=metodo_verificacion,
                    estado=True,
                    verificado=False,
                    rol_id=3  # Usuario regular por defecto
                )

                # Guardar en la base de datos usando el método save() del modelo
                nuevo_usuario.save()

                # Generar y enviar OTP
                otp_code = nuevo_usuario.generate_otp()

                if metodo_verificacion == 'email':
                    send_email(email, 'Código de verificación', f'Tu código es: {otp_code}')
                elif metodo_verificacion == 'sms' and telefono:
                    send_sms(telefono, f'Tu código de verificación: {otp_code}')

                session['user_email'] = email  # Guardamos el email sin encriptar en la sesión

                return jsonify({
                    'success': True,
                    'message': f'Código enviado a tu {metodo_verificacion}',
                    'show_otp_verification': True
                }), 200

            except Exception as e:
                return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500

        return jsonify({'success': False, 'message': 'Método no permitido'}), 405

    @staticmethod
    def verify_otp():
        if request.method == 'POST':
            try:
                data = request.get_json() if request.is_json else request.form
                email = session.get('user_email')  # Email sin encriptar de la sesión
                otp = data.get('otp')

                if not email or not otp:
                    return jsonify({'success': False, 'message': 'Datos incompletos'}), 400

                # Buscar usuario por email desencriptado
                usuario = Usuario.find_by_email(email)

                if not usuario:
                    return jsonify({
                        'success': False,
                        'message': 'Usuario no encontrado'
                    }), 404

                # Verificar OTP
                if usuario.verify_otp(otp):
                    session['user_id'] = usuario.id
                    session['user_role'] = usuario.rol_id

                    redirect_url = {
                        1: 'admin.dashboard',
                        2: 'agent.dashboard',
                        3: 'user.dashboard'
                    }.get(usuario.rol_id, 'auth.index')

                    return jsonify({
                        'success': True,
                        'message': 'Usuario verificado. Redirigiendo...',
                        'redirect': url_for(redirect_url)
                    }), 200
                else:
                    return jsonify({
                        'success': False,
                        'message': 'Código inválido o expirado'
                    }), 400

            except Exception as e:
                return jsonify({'success': False, 'message': str(e)}), 500

        return jsonify({'success': False, 'message': 'Método no permitido'}), 405

    @staticmethod
    def login():
        if request.method == 'GET':
            # Lógica para mostrar el formulario de login
            return render_template('index.html')
        
        if request.method == 'POST':
            try:
                data = request.get_json() if request.is_json else request.form
                email = data.get('email')
                password = data.get('password')

                if not all([email, password]):
                    return jsonify({
                        'success': False,
                        'message': 'Email y contraseña requeridos'
                    }), 400

                # Buscar usuario por email desencriptado
                usuario = Usuario.find_by_email(email)

                if not usuario or not usuario.estado:
                    return jsonify({
                        'success': False,
                        'message': 'Su cuenta ha sido desactivada / No se encuentra registrado'
                    }), 401

                # Verificar contraseña
                if not usuario.verify_password(password):
                    return jsonify({
                        'success': False,
                        'message': 'Credenciales inválidas'
                    }), 401

                # Verificación OTP si es necesario
                if not usuario.verificado:
                    otp_code = usuario.generate_otp()

                    if usuario.metodo_verificacion == 'email':
                        send_email(email, 'Verificación', f'Tu código: {otp_code}')
                    elif usuario.metodo_verificacion == 'sms' and usuario.telefono:
                        telefono_desencriptado = usuario.get_telefono_desencriptado()
                        send_sms(telefono_desencriptado, f'Código: {otp_code}')

                    session['user_email'] = email  # Email sin encriptar
                    return jsonify({
                        'success': True,
                        'message': 'Verificación requerida',
                        'show_otp_verification': True
                    }), 200

                # Login exitoso
                session['user_id'] = usuario.id
                session['user_email'] = email 
                session['user_role'] = usuario.rol_id
                
                # Actualizar último login
                usuario.update_login_timestamp()

                redirect_url = {
                    1: 'admin.dashboard',
                    2: 'agent.dashboard',
                    3: 'user.dashboard'
                }.get(usuario.rol_id, 'auth.index')

                return jsonify({
                    'success': True,
                    'message': 'Inicio de sesión exitoso',
                    'redirect': url_for(redirect_url)
                }), 200

            except Exception as e:
                return jsonify({
                    'success': False,
                    'message': f'Error en el servidor: {str(e)}'
                }), 500

        return jsonify({'success': False, 'message': 'Método no permitido'}), 405

    @staticmethod
    def logout():
        session.clear()
        return redirect(url_for('auth.index'))