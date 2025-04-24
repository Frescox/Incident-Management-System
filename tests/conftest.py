import pytest
from flask import Flask
from app import create_app
from app.models.core import db
from config import config
from app.models.auxiliary_models import LogActividad


@pytest.fixture
def app():
    """Crea y configura una instancia de la aplicación Flask para pruebas."""
    app = create_app('testing')
    
    # Usar la base de datos local (sin contraseña) para las pruebas
    app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'mysql+mysqlconnector://root@localhost/sistema_incidencias',
        'SQLALCHEMY_TRACK_MODIFICATIONS': False,  # Desactiva el seguimiento de modificaciones, para evitar advertencias
    })
    
    # Crear las tablas en la base de datos de prueba (en local)
    with app.app_context():
        db.create_all()
    
    yield app
    
    # Limpiar después de las pruebas
    with app.app_context():
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    """Cliente de prueba para la aplicación Flask."""
    return app.test_client()

@pytest.fixture
def runner(app):
    """Runner de prueba para comandos de Flask CLI."""
    return app.test_cli_runner()

@pytest.fixture
def init_database(app):
    """Inicializa la base de datos con datos de prueba en la base de datos local."""
    with app.app_context():
        # Crear datos de prueba
        from app.models.user_rol_models import Rol, Usuario
        from app.models.catalog_models import Estado, Prioridad, Categoria
        from app.utils.aes_encryption import encrypt
        
        # Roles
        admin_role = Rol(nombre='administrador', descripcion='Administrador')
        agent_role = Rol(nombre='agente', descripcion='Agente')
        user_role = Rol(nombre='usuario', descripcion='Usuario')
        
        db.session.add_all([admin_role, agent_role, user_role])
        db.session.commit()
        
        # Estados
        new_estado = Estado(nombre='nuevo', descripcion='Nuevo')
        progress_estado = Estado(nombre='en_progreso', descripcion='En progreso')
        resolved_estado = Estado(nombre='resuelto', descripcion='Resuelto')
        closed_estado = Estado(nombre='cerrado', descripcion='Cerrado')
        
        db.session.add_all([new_estado, progress_estado, resolved_estado, closed_estado])
        db.session.commit()
        
        # Prioridades
        high_priority = Prioridad(nombre='alta', descripcion='Alta')
        medium_priority = Prioridad(nombre='media', descripcion='Media')
        low_priority = Prioridad(nombre='baja', descripcion='Baja')
        
        db.session.add_all([high_priority, medium_priority, low_priority])
        db.session.commit()
        
        # Categorías
        hardware_category = Categoria(nombre='Hardware', descripcion='Hardware')
        software_category = Categoria(nombre='Software', descripcion='Software')
        network_category = Categoria(nombre='Redes', descripcion='Redes')
        
        db.session.add_all([hardware_category, software_category, network_category])
        db.session.commit()
        
        # Usuarios
        admin_user = Usuario(
            nombre=encrypt('Admin'),
            apellido=encrypt('Sistema'),
            email=encrypt('admin@sistema.com'),
            password=encrypt('adminsistema'),
            rol_id=1,
            estado=True,
            verificado=True
        )
        
        agent_user = Usuario(
            nombre=encrypt('Agente'),
            apellido=encrypt('Soporte'),
            email=encrypt('agente@sistema.com'),
            password=encrypt('agente123'),
            rol_id=2,
            estado=True,
            verificado=True
        )
        
        regular_user = Usuario(
            nombre=encrypt('Usuario'),
            apellido=encrypt('Regular'),
            email=encrypt('usuario@sistema.com'),
            password=encrypt('usuario123'),
            rol_id=3,
            estado=True,
            verificado=True
        )
        
        db.session.add_all([admin_user, agent_user, regular_user])
        db.session.commit()
        
        yield db
