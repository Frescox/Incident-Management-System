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

    # Relaciones
    categoria = db.relationship('Categoria', backref='incidencias')
    prioridad = db.relationship('Prioridad', backref='incidencias')
    estado = db.relationship('Estado', backref='incidencias')
    creador = db.relationship('Usuario', foreign_keys=[usuario_creador_id], 
              backref=db.backref('incidencias_creadas', lazy='dynamic'))
    asignado_a = db.relationship('Usuario', foreign_keys=[agente_asignado_id], 
                 backref=db.backref('incidencias_asignadas', lazy='dynamic'))
    comentarios = db.relationship('Comentario', backref='incidencia', cascade='all, delete-orphan')
    historial = db.relationship('HistorialEstado', backref='incidencia', cascade='all, delete-orphan')

    @classmethod
    def get_by_id(cls, id):
        return cls.query.get(id)

    @classmethod
    def get_by_user(cls, user_id):
        return cls.query.filter_by(usuario_creador_id=user_id).order_by(cls.fecha_creacion.desc()).all()

    @classmethod
    def get_by_agent(cls, agent_id):
        return cls.query.filter_by(agente_asignado_id=agent_id).order_by(cls.fecha_creacion.desc()).all()
    
    def save(self):
        """
        Guarda los cambios realizados a la incidencia en la base de datos
        """
        try:
            db.session.add(self)
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            print(f"Error al guardar incidencia: {str(e)}")
            return False
    
    def change_status(self, new_estado_id, usuario_id, comentario=None):
        """
        Cambia el estado de una incidencia y registra el cambio en el historial
        """
        from app.models.ticket_models import HistorialEstado
        
        # Guardar el estado anterior
        estado_anterior_id = self.estado_id
        
        # Cambiar al nuevo estado
        self.estado_id = new_estado_id
        self.fecha_ultima_actualizacion = datetime.utcnow()
        
        # Si el nuevo estado es "resuelto", actualizar fecha de resolución
        if int(new_estado_id) == 3:
            self.fecha_resolucion = datetime.utcnow()
        
        # Si el nuevo estado es "cerrado", actualizar fecha de cierre
        if int(new_estado_id) == 4:
            self.fecha_cierre = datetime.utcnow()
        
        # Registrar el cambio en el historial
        historial = HistorialEstado(
            incidencia_id=self.id,
            estado_anterior_id=estado_anterior_id,
            estado_nuevo_id=new_estado_id,
            usuario_id=usuario_id,
            comentario=comentario
        )
        
        # Guardar el historial
        try:
            db.session.add(historial)
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            print(f"Error al registrar cambio de estado: {str(e)}")
            return False
    
    @classmethod
    def get_by_id_with_details(cls, id):
        return cls.query.filter_by(id=id)\
            .options(
                db.joinedload(cls.categoria),
                db.joinedload(cls.prioridad),
                db.joinedload(cls.estado),
                db.joinedload(cls.creador),
                db.joinedload(cls.asignado_a)
            ).first()
    
class Comentario(BaseModel):
    __tablename__ = 'comentarios'
    
    id = db.Column(db.Integer, primary_key=True)
    incidencia_id = db.Column(db.Integer, db.ForeignKey('incidencias.id', ondelete='CASCADE'), nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    contenido = db.Column(db.Text, nullable=False)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)

    usuario = db.relationship('Usuario', backref='comentarios')
    
    @classmethod
    def get_by_incident(cls, incident_id):
        """Obtener los comentarios de una incidencia ordenados por fecha de creación"""
        return cls.query.filter_by(incidencia_id=incident_id).order_by(cls.fecha_creacion.desc()).all()
    
    def save(self):
        try:
            db.session.add(self)
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            print(f"Error al guardar comentario: {str(e)}")
            return False

class HistorialEstado(db.Model):
    __tablename__ = 'historial_estados'
    
    id = db.Column(db.Integer, primary_key=True)
    incidencia_id = db.Column(db.Integer, db.ForeignKey('incidencias.id', ondelete='CASCADE'), nullable=False)
    estado_anterior_id = db.Column(db.Integer, db.ForeignKey('estados.id'), nullable=False)
    estado_nuevo_id = db.Column(db.Integer, db.ForeignKey('estados.id'), nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    comentario = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    estado_anterior = db.relationship('Estado', foreign_keys=[estado_anterior_id])
    estado_nuevo = db.relationship('Estado', foreign_keys=[estado_nuevo_id])
    usuario = db.relationship('Usuario', backref='cambios_estado')
    
    @classmethod
    def get_by_incident(cls, incident_id):
        """Obtener el historial de estados de una incidencia ordenado por fecha de creación descendente"""
        return cls.query.filter_by(incidencia_id=incident_id).order_by(cls.created_at.desc()).all()
    
    def save(self):
        try:
            db.session.add(self)
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            print(f"Error al guardar historial: {str(e)}")
            return False