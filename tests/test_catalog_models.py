import pytest
from app.models.catalog_models import Categoria, Prioridad, Estado, CategoriaAgente
from app.models.user_models import Usuario

class TestCategoriaModel:
    """Pruebas para el modelo Categoria."""
    
    def test_get_all(self, app, init_database):
        """Prueba la obtención de todas las categorías."""
        with app.app_context():
            # Obtener todas las categorías
            categorias = Categoria.get_all()
            
            # Verificar que se hayan recuperado categorías
            assert len(categorias) > 0
            
            # Verificar que sean instancias de Categoria
            assert all(isinstance(cat, Categoria) for cat in categorias)
            
            # Verificar que estén ordenadas por nombre
            for i in range(len(categorias) - 1):
                assert categorias[i].nombre <= categorias[i+1].nombre
    
    def test_get_by_id(self, app, init_database):
        """Prueba la obtención de una categoría por ID."""
        with app.app_context():
            # Obtener una categoría (ID 1 = Hardware)
            categoria = Categoria.get_by_id(1)
            
            # Verificar que se haya recuperado correctamente
            assert categoria is not None
            assert categoria.id == 1
            assert categoria.nombre == 'Hardware'
            
            # Intentar obtener una categoría inexistente
            categoria_inexistente = Categoria.get_by_id(999)
            assert categoria_inexistente is None

class TestPrioridadModel:
    """Pruebas para el modelo Prioridad."""
    
    def test_get_all(self, app, init_database):
        """Prueba la obtención de todas las prioridades."""
        with app.app_context():
            # Obtener todas las prioridades
            prioridades = Prioridad.get_all()
            
            # Verificar que se hayan recuperado prioridades
            assert len(prioridades) > 0
            
            # Verificar que sean instancias de Prioridad
            assert all(isinstance(pri, Prioridad) for pri in prioridades)
            
            # Verificar que estén ordenadas por ID
            for i in range(len(prioridades) - 1):
                assert prioridades[i].id <= prioridades[i+1].id
    
    def test_get_by_id(self, app, init_database):
        """Prueba la obtención de una prioridad por ID."""
        with app.app_context():
            # Obtener una prioridad (ID 1 = alta)
            prioridad = Prioridad.get_by_id(1)
            
            # Verificar que se haya recuperado correctamente
            assert prioridad is not None
            assert prioridad.id == 1
            assert prioridad.nombre == 'alta'
            
            # Intentar obtener una prioridad inexistente
            prioridad_inexistente = Prioridad.get_by_id(999)
            assert prioridad_inexistente is None

class TestEstadoModel:
    """Pruebas para el modelo Estado."""
    
    def test_get_all(self, app, init_database):
        """Prueba la obtención de todos los estados."""
        with app.app_context():
            # Obtener todos los estados
            estados = Estado.get_all()
            
            # Verificar que se hayan recuperado estados
            assert len(estados) > 0
            
            # Verificar que sean instancias de Estado
            assert all(isinstance(est, Estado) for est in estados)
            
            # Verificar que estén ordenados por ID
            for i in range(len(estados) - 1):
                assert estados[i].id <= estados[i+1].id
    
    def test_get_by_id(self, app, init_database):
        """Prueba la obtención de un estado por ID."""
        with app.app_context():
            # Obtener un estado (ID 1 = nuevo)
            estado = Estado.get_by_id(1)
            
            # Verificar que se haya recuperado correctamente
            assert estado is not None
            assert estado.id == 1
            assert estado.nombre == 'nuevo'
            
            # Intentar obtener un estado inexistente
            estado_inexistente = Estado.get_by_id(999)
            assert estado_inexistente is None

class TestCategoriaAgenteModel:
    """Pruebas para el modelo CategoriaAgente."""
    
    def test_create_categoria_agente(self, app, init_database):
        """Prueba la creación de una relación entre agente y categoría."""
        with app.app_context():
            db = init_database
            
            # Obtener un agente
            agente = Usuario.find_by_email('agente@sistema.com')
            
            # Obtener una categoría
            categoria = Categoria.get_by_id(1)  # Hardware
            
            # Crear la relación
            categoria_agente = CategoriaAgente(
                usuario_id=agente.id,
                categoria_id=categoria.id
            )
            
            # Guardar en la base de datos
            db.session.add(categoria_agente)
            db.session.commit()
            
            # Verificar que se haya creado correctamente
            nueva_relacion = CategoriaAgente.query.filter_by(
                usuario_id=agente.id,
                categoria_id=categoria.id
            ).first()
            
            assert nueva_relacion is not None
            assert nueva_relacion.usuario_id == agente.id
            assert nueva_relacion.categoria_id == categoria.id
    
    def test_categoria_relationship(self, app, init_database):
        """Prueba la relación con el modelo Categoria."""
        with app.app_context():
            db = init_database
            
            # Obtener un agente
            agente = Usuario.find_by_email('agente@sistema.com')
            
            # Obtener una categoría
            categoria = Categoria.get_by_id(2)  # Software
            
            # Crear la relación
            categoria_agente = CategoriaAgente(
                usuario_id=agente.id,
                categoria_id=categoria.id
            )
            
            # Guardar en la base de datos
            db.session.add(categoria_agente)
            db.session.commit()
            
            # Verificar la relación con la categoría
            relacion = CategoriaAgente.query.filter_by(
                usuario_id=agente.id,
                categoria_id=categoria.id
            ).first()
            
            assert relacion is not None
            assert relacion.categoria is not None
            assert relacion.categoria.id == categoria.id
            assert relacion.categoria.nombre == categoria.nombre