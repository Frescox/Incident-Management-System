from .core import db, BaseModel

class Categoria(BaseModel):
    __tablename__ = 'categorias'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), unique=True, nullable=False)
    descripcion = db.Column(db.Text)

    @classmethod
    def get_all(cls):
        return cls.query.order_by(cls.nombre).all()

    @classmethod
    def get_by_id(cls, id):
        return cls.query.get(id)

class Prioridad(BaseModel):
    __tablename__ = 'prioridades'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), unique=True, nullable=False)
    descripcion = db.Column(db.Text)

    @classmethod
    def get_all(cls):
        return cls.query.order_by(cls.id).all()

    @classmethod
    def get_by_id(cls, id):
        return cls.query.get(id)

class Estado(BaseModel):
    __tablename__ = 'estados'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), unique=True, nullable=False)
    descripcion = db.Column(db.Text)

    @classmethod
    def get_all(cls):
        return cls.query.order_by(cls.id).all()

    @classmethod
    def get_by_id(cls, id):
        return cls.query.get(id)

class CategoriaAgente(BaseModel):
    __tablename__ = 'categoria_agente'
    
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id', ondelete='CASCADE'), nullable=False)
    categoria_id = db.Column(db.Integer, db.ForeignKey('categorias.id', ondelete='CASCADE'), nullable=False)
    
    categoria = db.relationship('Categoria', backref='agentes_asignados')