from .core import db, BaseModel

# Estas relaciones se mantienen en los otros archivos donde están los modelos relacionados

class Rol(BaseModel):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), unique=True, nullable=False)
    descripcion = db.Column(db.Text)
    usuarios = db.relationship('Usuario', backref='rol', lazy=True)

class Usuario(BaseModel):
    __tablename__ = 'usuarios'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    apellido = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    rol_id = db.Column(db.Integer, db.ForeignKey('roles.id'), nullable=False)
    estado = db.Column(db.Boolean, default=True)
    ultimo_login = db.Column(db.DateTime)

    incidencias_creadas = db.relationship('Incidencia', foreign_keys='Incidencia.usuario_creador_id', backref='creador')
    incidencias_asignadas = db.relationship('Incidencia', foreign_keys='Incidencia.agente_asignado_id', backref='agente')
    comentarios = db.relationship('Comentario', backref='usuario')
    cambios_estado = db.relationship('HistorialEstado', backref='usuario')