from .core import db, BaseModel

class Adjunto(BaseModel):
    __tablename__ = 'adjuntos'
    id = db.Column(db.Integer, primary_key=True)
    incidencia_id = db.Column(db.Integer, db.ForeignKey('incidencias.id', ondelete='CASCADE'), nullable=False)
    nombre_archivo = db.Column(db.String(255), nullable=False)
    ruta_archivo = db.Column(db.String(255), nullable=False)
    tipo_archivo = db.Column(db.String(100), nullable=False)
    tamaño_archivo = db.Column(db.Integer, nullable=False)

class Comentario(BaseModel):
    __tablename__ = 'comentarios'
    id = db.Column(db.Integer, primary_key=True)
    incidencia_id = db.Column(db.Integer, db.ForeignKey('incidencias.id', ondelete='CASCADE'), nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    contenido = db.Column(db.Text, nullable=False)

class LogActividad(BaseModel):
    __tablename__ = 'log_actividad'
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id', ondelete='SET NULL'), nullable=True)
    accion = db.Column(db.String(255), nullable=False)
    entidad = db.Column(db.String(50), nullable=True)
    entidad_id = db.Column(db.Integer, nullable=True)
    detalles = db.Column(db.Text, nullable=True)
    ip_address = db.Column(db.String(45), nullable=True)
    user_agent = db.Column(db.Text, nullable=True)