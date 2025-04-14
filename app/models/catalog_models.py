from .core import db, BaseModel

class Categoria(BaseModel):
    __tablename__ = 'categorias'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), unique=True, nullable=False)
    descripcion = db.Column(db.Text)
    incidencias = db.relationship('Incidencia', backref='categoria', lazy=True)

class Prioridad(BaseModel):
    __tablename__ = 'prioridades'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), unique=True, nullable=False)
    descripcion = db.Column(db.Text)
    incidencias = db.relationship('Incidencia', backref='prioridad', lazy=True)

class Estado(BaseModel):
    __tablename__ = 'estados'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), unique=True, nullable=False)
    descripcion = db.Column(db.Text)
    incidencias = db.relationship('Incidencia', backref='estado', lazy=True)

class CategoriaAgente(BaseModel):
    __tablename__ = 'categoria_agente'
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id', ondelete='CASCADE'), nullable=False)
    categoria_id = db.Column(db.Integer, db.ForeignKey('categorias.id', ondelete='CASCADE'), nullable=False)