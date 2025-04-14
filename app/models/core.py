from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class BaseModel(db.Model):
    __abstract__ = True
    created_at = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp())
    updated_at = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())