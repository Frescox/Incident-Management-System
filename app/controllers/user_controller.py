from flask import render_template, session, redirect, url_for
from app.models.user import Usuario
from app.utils.aes_encryption import decrypt  # Para desencriptar los datos

class UserController:
    @staticmethod
    def dashboard():
        # Verifica si hay un usuario en sesión
        if 'user_email' not in session:
            return redirect(url_for('auth.index'))

        # Obtener el usuario por email desde la base de datos
        usuario = Usuario.find_by_email(session['user_email'])
        if not usuario:
            return redirect(url_for('auth.index'))

        # Desencriptar nombre, apellido, etc.
        nombre = decrypt(usuario.nombre)
        apellido = decrypt(usuario.apellido)
        correo = session.get('user_email')  # Ya lo guardaste sin encriptar

        # Enviar los datos al HTML
        return render_template('user_dashboard.html', nombre=nombre, apellido=apellido, correo=correo)
