from datetime import datetime
from .core import db, BaseModel

class Incidencia(BaseModel):
    __tablename__ = 'incidencias'
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(255), nullable=False)
    descripcion = db.Column(db.Text, nullable=False)
    categoria_id = db.Column(db.Integer, db.ForeignKey('categorias.id'), nullable=False)
    prioridad_id = db.Column(db.Integer, db.ForeignKey('prioridades.id'), nullable=False)
    estado_id = db.Column(db.Integer, db.ForeignKey('estados.id'), nullable=False)
    usuario_creador_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    agente_asignado_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=True)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    fecha_ultima_actualizacion = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    fecha_resolucion = db.Column(db.DateTime, nullable=True)
    fecha_cierre = db.Column(db.DateTime, nullable=True)

    adjuntos = db.relationship('Adjunto', backref='incidencia', cascade='all, delete-orphan')
    comentarios = db.relationship('Comentario', backref='incidencia', cascade='all, delete-orphan')
    historial_estados = db.relationship('HistorialEstado', backref='incidencia', cascade='all, delete-orphan')

class HistorialEstado(BaseModel):
    __tablename__ = 'historial_estados'
    id = db.Column(db.Integer, primary_key=True)
    incidencia_id = db.Column(db.Integer, db.ForeignKey('incidencias.id', ondelete='CASCADE'), nullable=False)
    estado_anterior_id = db.Column(db.Integer, db.ForeignKey('estados.id'), nullable=False)
    estado_nuevo_id = db.Column(db.Integer, db.ForeignKey('estados.id'), nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    comentario = db.Column(db.Text, nullable=True)