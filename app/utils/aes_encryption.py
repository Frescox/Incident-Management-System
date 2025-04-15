from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
import base64
import hashlib

# Crea una clave de 32 bytes (256 bits) desde un string
KEY = hashlib.sha256(b'123').digest()

def pad(text):
    return text + (16 - len(text) % 16) * ' '

def encrypt(text):
    iv = get_random_bytes(16)
    cipher = AES.new(KEY, AES.MODE_CBC, iv)
    padded_text = pad(text)
    encrypted = cipher.encrypt(padded_text.encode('utf-8'))
    return base64.b64encode(iv + encrypted).decode('utf-8')

def decrypt(encrypted_text):
    raw = base64.b64decode(encrypted_text)
    iv = raw[:16]
    cipher = AES.new(KEY, AES.MODE_CBC, iv)
    decrypted = cipher.decrypt(raw[16:]).decode('utf-8')
    return decrypted.strip()
