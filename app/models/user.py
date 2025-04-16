from app.db.database import db
from datetime import datetime
import hashlib
import os
import time
import random
from app.utils.aes_encryption import encrypt, decrypt

class Usuario:
    def __init__(self, id=None, nombre="", apellido="", email="", password="", rol_id=3, estado=True,
                 telefono=None, metodo_verificacion=None, otp=None, otp_expira=None, verificado=False):
        self.id = id
        self.nombre = nombre
        self.apellido = apellido
        self.email = email
        self.password = password
        self.rol_id = rol_id
        self.estado = estado
        self.ultimo_login = None
        self.telefono = telefono
        self.metodo_verificacion = metodo_verificacion
        self.otp = otp
        self.otp_expira = otp_expira
        self.verificado = verificado
        self.created_at = datetime.now()
        self.updated_at = datetime.now()

    def save(self):
        conn = db.get_connection()
        if not conn:
            return None
        cursor = conn.cursor()

        password_encrypted = self.password

        if self.id is None:
            query = """
            INSERT INTO usuarios (nombre, apellido, email, password, rol_id, estado, telefono, 
                                metodo_verificacion, otp, otp_expira, verificado)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(query, (self.nombre, self.apellido, self.email, password_encrypted, 
                                self.rol_id, self.estado, self.telefono, self.metodo_verificacion,
                                self.otp, self.otp_expira, self.verificado))
            self.id = cursor.lastrowid
        else:
            query = """
            UPDATE usuarios 
            SET nombre=%s, apellido=%s, email=%s, password=%s, rol_id=%s, estado=%s,
                telefono=%s, metodo_verificacion=%s, otp=%s, otp_expira=%s, verificado=%s,
                updated_at=CURRENT_TIMESTAMP
            WHERE id=%s
            """
            cursor.execute(query, (self.nombre, self.apellido, self.email, password_encrypted, 
                                self.rol_id, self.estado, self.telefono, self.metodo_verificacion,
                                self.otp, self.otp_expira, self.verificado, self.id))
        
        conn.commit()
        cursor.close()
        conn.close()
        return self.id

    @staticmethod
    def find_by_email(email):
        conn = db.get_connection()
        if not conn:
            return None
        cursor = conn.cursor(dictionary=True)
        
        query = "SELECT * FROM usuarios"
        cursor.execute(query)
        
        for result in cursor.fetchall():
            try:
                decrypted_email = decrypt(result['email']) if result['email'] else ""
                if decrypted_email == email:
                    usuario = Usuario(
                        id=result['id'],
                        nombre=result['nombre'],
                        apellido=result['apellido'],
                        email=result['email'], 
                        password=result['password'],
                        rol_id=result['rol_id'],
                        estado=result['estado'],
                        telefono=result['telefono'],
                        metodo_verificacion=result.get('metodo_verificacion'),
                        otp=result.get('otp'),
                        otp_expira=result.get('otp_expira'),
                        verificado=result.get('verificado', False)
                    )
                    usuario.ultimo_login = result.get('ultimo_login')
                    usuario.created_at = result.get('created_at')
                    usuario.updated_at = result.get('updated_at')
                    cursor.close()
                    conn.close()
                    return usuario
            except Exception as e:
                print(f"[ERROR] Falló la desencriptación de email: {e}")
                continue

        cursor.close()
        conn.close()
        return None

    def verify_password(self, password):
        if not self.password:
            return False
        try:
            password_desencriptado = decrypt(self.password)
            return password == password_desencriptado
        except Exception as e:
            print(f"[ERROR] Falló la desencriptación de contraseña: {e}")
            return False

    def get_nombre_desencriptado(self):
        return decrypt(self.nombre) if self.nombre else ""
    
    def get_apellido_desencriptado(self):
        return decrypt(self.apellido) if self.apellido else ""
    
    def get_telefono_desencriptado(self):
        return decrypt(self.telefono) if self.telefono else None
    
    def generate_otp(self):
        self.otp = str(int(random.random() * 1000000)).zfill(6)
        self.otp_expira = int(time.time()) + 900
        self.save()
        return self.otp
    
    def verify_otp(self, otp):
        current_time = int(time.time())
        if not self.otp or not self.otp_expira:
            return False
        if self.otp == otp and current_time <= self.otp_expira:
            self.verificado = True
            self.otp = None
            self.otp_expira = None
            self.save()
            return True
        return False
    
    def update_login_timestamp(self):
        if not self.id:
            return
        conn = db.get_connection()
        if not conn:
            return
        cursor = conn.cursor()
        
        query = "UPDATE usuarios SET ultimo_login=CURRENT_TIMESTAMP WHERE id=%s"
        cursor.execute(query, (self.id,))
        
        conn.commit()
        cursor.close()
        conn.close()
