from flask import request, jsonify, session, redirect, url_for, render_template
from app.models.user import Usuario
from app.services.mail_service import send_email
from app.services.sms_service import send_sms
from app.utils.aes_encryption import encrypt, decrypt
from app.db.database import db

class AuthController:
    @staticmethod
    def index():
        """Renderiza la página principal de autenticación"""
        return render_template('index.html')

    @staticmethod
    def register():
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

                # Buscar usuario por email (incluyendo desactivados)
                conn = db.get_connection()
                cursor = conn.cursor(dictionary=True)
                cursor.execute("SELECT email FROM usuarios")
                existing_users = cursor.fetchall()
                cursor.close()
                conn.close()

                # Verificar si el email ya existe
                for user in existing_users:
                    try:
                        if decrypt(user['email']) == email:
                            return jsonify({'success': False, 'message': 'El correo ya está registrado'}), 400
                    except:
                        continue

                # Crear nuevo usuario
                nuevo_usuario = Usuario(
                    nombre=encrypt(nombre),
                    apellido=encrypt(apellido),
                    email=encrypt(email),
                    password=encrypt(password),
                    telefono=encrypt(telefono) if telefono else None,
                    metodo_verificacion=metodo_verificacion,
                    estado=True,
                    verificado=False
                )

                # Generar y enviar OTP
                otp = nuevo_usuario.generate_otp()
                if metodo_verificacion == 'email':
                    send_email(email, 'Código de verificación', f'Tu código es: {otp}')
                elif metodo_verificacion == 'sms' and telefono:
                    send_sms(telefono, f'Tu código de verificación: {otp}')

                nuevo_usuario.save()
                session['user_email'] = email

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
                email = session.get('user_email')
                otp = data.get('otp')

                if not email or not otp:
                    return jsonify({'success': False, 'message': 'Datos incompletos'}), 400

                # Buscar usuario
                conn = db.get_connection()
                cursor = conn.cursor(dictionary=True)
                cursor.execute("SELECT * FROM usuarios WHERE email = %s", (encrypt(email),))
                user_data = cursor.fetchone()
                cursor.close()
                conn.close()

                if not user_data:
                    return jsonify({'success': False, 'message': 'Usuario no encontrado'}), 404

                usuario = Usuario(
                    id=user_data['id'],
                    nombre=user_data['nombre'],
                    apellido=user_data['apellido'],
                    email=user_data['email'],
                    password=user_data['password'],
                    rol_id=user_data['rol_id'],
                    estado=user_data['estado'],
                    otp=user_data.get('otp'),
                    otp_expira=user_data.get('otp_expira'),
                    verificado=user_data.get('verificado', False)
                )

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

                # Obtener todos los usuarios
                conn = db.get_connection()
                cursor = conn.cursor(dictionary=True)
                cursor.execute("SELECT * FROM usuarios")
                users = cursor.fetchall()
                cursor.close()
                conn.close()

                # Buscar usuario por email
                usuario_encontrado = None
                for user in users:
                    try:
                        if decrypt(user['email']) == email:
                            usuario_encontrado = user
                            break
                    except:
                        continue

                if not usuario_encontrado:
                    return jsonify({
                        'success': False,
                        'message': 'Credenciales inválidas'
                    }), 401

                # Verificar estado
                if not usuario_encontrado['estado']:
                    return jsonify({
                        'success': False,
                        'message': 'Cuenta desactivada. Contacta al administrador.'
                    }), 403

                # Verificar contraseña
                try:
                    if password != decrypt(usuario_encontrado['password']):
                        return jsonify({
                            'success': False,
                            'message': 'Credenciales inválidas'
                        }), 401
                except:
                    return jsonify({
                        'success': False,
                        'message': 'Error procesando tu contraseña'
                    }), 500

                # Crear objeto usuario
                usuario = Usuario(
                    id=usuario_encontrado['id'],
                    nombre=usuario_encontrado['nombre'],
                    apellido=usuario_encontrado['apellido'],
                    email=usuario_encontrado['email'],
                    password=usuario_encontrado['password'],
                    rol_id=usuario_encontrado['rol_id'],
                    estado=usuario_encontrado['estado'],
                    verificado=usuario_encontrado.get('verificado', False),
                    metodo_verificacion=usuario_encontrado.get('metodo_verificacion')
                )

                # Verificación OTP si es necesario
                if not usuario.verificado:
                    otp = usuario.generate_otp()
                    if usuario.metodo_verificacion == 'email':
                        send_email(email, 'Verificación', f'Tu código: {otp}')
                    elif usuario.metodo_verificacion == 'sms' and usuario.telefono:
                        send_sms(decrypt(usuario.telefono), f'Código: {otp}')

                    session['user_email'] = email
                    return jsonify({
                        'success': True,
                        'message': 'Verificación requerida',
                        'show_otp_verification': True
                    }), 200

                # Login exitoso
                session['user_id'] = usuario.id
                session['user_email'] = email
                session['user_role'] = usuario.rol_id
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