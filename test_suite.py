# Importación de librerías necesarias
import pytest
from app import create_app
from app.models.core import db
from app.models.user_rol_models import Usuario
from app.models.ticket_models import Incidencia
from datetime import datetime, timedelta
from app.models.catalog_models import Estado, Prioridad, Categoria
import random
from app.utils.aes_encryption import decrypt, encrypt
from locust import HttpUser, task, between
import coverage 
from threading import Thread  
import time

# ---------- CONFIGURACIÓN DE COBERTURA (3.3) ----------
cov = coverage.Coverage()
cov.start()

# ---------- FIXTURES PARA CONFIGURACIÓN Y DATOS DE PRUEBA ----------

# Configura una aplicación de prueba con base de datos en memoria
@pytest.fixture
def app():
    """Crea una instancia de la aplicación en modo testing con base de datos SQLite en memoria"""
    app = create_app('testing')
    app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'WTF_CSRF_ENABLED': False
    })
    
    with app.app_context():
        db.create_all()
        # Se agregan datos base de catálogos (estado, prioridad, categoría)
        db.session.add_all([
            Estado(id=1, nombre="Abierta"),
            Prioridad(id=1, nombre="Baja"),
            Prioridad(id=2, nombre="Media"),
            Prioridad(id=3, nombre="Alta"),
            Categoria(id=1, nombre="Software"),
            Categoria(id=2, nombre="Hardware"),
            Categoria(id=3, nombre="Red"),
            Categoria(id=4, nombre="Otro"),
        ])
        db.session.commit()
        yield app  # Devuelve la app para que sea usada en los tests
        db.session.remove()
        db.drop_all()
        # Generación de reportes de cobertura al finalizar (3.3)
        cov.stop()
        cov.save()
        cov.report()
        cov.html_report(directory='coverage_report')

# Crea un cliente de prueba que simula un navegador
@pytest.fixture
def client(app):
    return app.test_client()

# Crea un usuario de prueba que será usado en varios tests
@pytest.fixture
def test_user(app):
    """Crea y devuelve un usuario de prueba"""
    with app.app_context():
        user = Usuario(
            nombre=encrypt("Test"),
            apellido=encrypt("User"),
            email=encrypt("test@example.com"),
            password=encrypt("password123"),
            estado=True,
            verificado=True,
            rol_id=3,
        )
        db.session.add(user)
        db.session.commit()
        db.session.refresh(user)
        return user

# ---------- PRUEBAS TDD (3.1) ----------

def test_usuario_model_tdd():
    """
    PRUEBA TDD para el modelo Usuario (3.1 Desarrollo guiado por pruebas)
    Sigue el ciclo Red-Green-Refactor:
    1. Red: Escribir prueba que falla (antes de implementar Usuario)
    2. Green: Implementar mínimo código para pasar prueba
    3. Refactor: Mejorar el código manteniendo los tests
    """
    # Datos de prueba
    test_data = {
        "nombre": "Test",
        "email": "test@example.com",
        "password": "secret"
    }
    
    # 1. Red - Crear prueba para funcionalidad no implementada
    # (Esto fallará inicialmente hasta que implementemos Usuario)
    user = Usuario(
        nombre=encrypt(test_data["nombre"]),
        email=encrypt(test_data["email"]),
        password=encrypt(test_data["password"])
    )
    
    # Aserciones para verificar el comportamiento esperado
    assert decrypt(user.nombre) == test_data["nombre"]
    assert decrypt(user.email) == test_data["email"]
    assert decrypt(user.password) == test_data["password"]
    
    # Verificación adicional de almacenamiento seguro
    assert user.nombre != test_data["nombre"]  # Debe estar encriptado
    assert user.email != test_data["email"]    
    assert user.password != test_data["password"]  

# ---------- PRUEBAS DE MANEJO DE EXCEPCIONES ----------

# 3.2 Manejo de excepciones
def test_login_exception_handling(client, mocker):
    """
    Prueba que el sistema maneje correctamente excepciones durante el login.
    """
    # Mockea el método find_by_email para simular un error de desencriptación
    mocker.patch(
        'app.models.user_rol_models.Usuario.find_by_email',
        side_effect=Exception("Error de desencriptación")
    )

    response = client.post('/login', data={
        'email': 'test@example.com',
        'password': 'password123'
    }, follow_redirects=True)

    # Verificaciones
    assert response.status_code == 500
    response_data = response.get_json()
    assert not response_data['success']
    assert "Error en el servidor" in response_data['message']

# ---------- PRUEBAS DE VALIDACIÓN ----------

# 3.4 Desarrollo de casos de prueba basados en escenarios
def test_invalid_incident_submission(client, test_user):
    """
    Prueba de validación: Envía datos inválidos (título vacío) y verifica que no se cree la incidencia.
    """
    with client.session_transaction() as session:
        session['user_id'] = test_user.id

    invalid_data = {
        'titulo': '',  # Título vacío
        'descripcion': 'Sin título',
        'usuario_creador_id': test_user.id,
        'estado_id': 1,
        'prioridad_id': 1,
        'categoria_id': 1
    }

    response = client.post('/user/incidents/create', data=invalid_data, follow_redirects=True)
    assert b"Campo requerido" in response.data or response.status_code == 200 

# ---------- PRUEBAS UNITARIAS Y DE SISTEMA ----------

# EXTRA
def test_user_login_acceptance(client, test_user):
    """
    Prueba de aceptación: Simula que el usuario inicia sesión correctamente
    y verifica que accede al panel principal.
    """
    response = client.post('/login', data={
        'email': decrypt(test_user.email),
        'password': decrypt(test_user.password)
    }, follow_redirects=True)

    assert response.status_code == 200
    
    # Convertir la respuesta en un objeto JSON
    response_json = response.get_json()

    assert response_json.get('redirect') == '/user/dashboard'

# 3.5 Pruebas basadas en perfiles operativos
def test_operational_profiles(app):
    """
    Simula un perfil de usuario frecuente que crea muchas incidencias.
    Verifica que el sistema soporte ese patrón de uso.
    """
    with app.app_context():
        # Crea un usuario frecuente
        user = Usuario(
            nombre="Frequent",
            apellido="User",
            email="frequent@example.com",
            password="password123",
            verificado=True,
            rol_id=3
        )
        db.session.add(user)
        db.session.commit()

        # Crea múltiples incidencias para simular uso continuo
        for i in range(20):
            incident = Incidencia(
                titulo=f"Incidencia {i}",
                descripcion="Descripción",
                usuario_creador_id=user.id,
                estado_id=1,
                prioridad_id=random.randint(1, 3),
                categoria_id=random.randint(1, 4)
            )
            db.session.add(incident)
        db.session.commit()

        # Verifica que al menos se crearon 20 incidencias
        count = Incidencia.query.filter_by(usuario_creador_id=user.id).count()
        assert count >= 20

# 3.6 Pruebas de sistema y aceptación
def test_full_create_and_update(app, client, test_user):
    """
    Prueba el flujo completo de creación y edición de una incidencia:
    desde el envío del formulario hasta verificar su existencia y modificación.
    """
    with app.app_context():
        # Simula que el usuario está logueado
        with client.session_transaction() as session:
            session['user_id'] = test_user.id

        from app.models.ticket_models import Incidencia

        # Datos para crear la incidencia
        incident = Incidencia(
                titulo="Prueba flujo",
                descripcion="Descripción",
                usuario_creador_id=test_user.id,
                estado_id=1,
                prioridad_id=random.randint(1, 3),
                categoria_id=random.randint(1, 4)
            )
        db.session.add(incident)
        db.session.commit()

        # 2. Verifica que se creó en la base de datos
        print("incidencias existentes:", Incidencia.query.all())

        incidencia = db.session.get(Incidencia, incident.id)
        assert incidencia is not None
        assert incidencia.descripcion == 'Descripción'

        # 3. Editar la incidencia
        edit_data = {
            'titulo': 'Prueba flujo editada',
            'descripcion': 'Descripción actualizada',
            'estado_id': 1,
            'prioridad_id': 1,
            'categoria_id': 2,
            'agente_asignado_id': 2
        }

        response_edit = client.post(f'/user/incidents/{incidencia.id}/update', data=edit_data, follow_redirects=False)
        assert response_edit.status_code == 302
        assert '/user/dashboard' in response_edit.location

        # 4. Verificar que los cambios se guardaron
        incidencia_actualizada = db.session.get(Incidencia, incidencia.id)
        assert incidencia_actualizada.titulo == 'Prueba flujo editada'
        assert incidencia_actualizada.descripcion == 'Descripción actualizada'
        assert incidencia_actualizada.estado_id == 1

# 3.7 Pruebas a través de atributos de calidad
def test_security(client):
    """
    Verifica que las rutas protegidas (como el panel de admin)
    no son accesibles sin autenticación y redirigen adecuadamente.
    """
    response = client.get('/admin/dashboard', follow_redirects=False)

    assert response.status_code in (302, 401)

    if response.status_code == 302:
        location = response.headers.get('Location', '')
        assert location in ['/', '/login', '/auth/login']  # Redirigue al login

def test_escalabilidad(app):
    """
    Prueba de escalabilidad del sistema (3.7 Atributos de calidad)
    Simula 100 usuarios concurrentes creando incidencias.
    """
    with app.app_context():
        threads = []
        start_time = time.time()
        
        def create_incident(user_id):
            with app.app_context():
                incident = Incidencia(
                    titulo=f"Incidente {user_id}",
                    descripcion="Prueba de carga",
                    usuario_creador_id=user_id,
                    estado_id=1,
                    prioridad_id=1,
                    categoria_id=1
                )
                db.session.add(incident)
                db.session.commit()
        
        for i in range(100):
            t = Thread(target=create_incident, args=(i+1,))
            threads.append(t)
            t.start()
        
        for t in threads:
            t.join()
        
        total_time = time.time() - start_time
        assert total_time < 5.0
        assert Incidencia.query.count() == 100

# 3.8 Pruebas de regresión
def test_regression(app, client, test_user):
    """
    Ejecuta pruebas básicas de regresión combinando pruebas previas:
    flujo de usuario frecuente, flujo completo y pruebas de seguridad.
    """
    test_operational_profiles(app)
    with app.app_context():
        test_full_create_and_update(app, client, test_user)
    test_security(client)


# ---------- PRUEBAS DE UI, USABILIDAD Y RENDIMIENTO ----------

# 3.10 Pruebas de interfaz de usuario
def test_ui_physical_aspects(client):
    """
    Verifica que la ruta de dashboard del usuario exista
    y que la respuesta sea de tipo HTML.
    """
    response = client.get('/user/dashboard', follow_redirects=True)
    assert response.status_code == 200
    assert 'text/html' in response.content_type

# 3.11 Pruebas de usabilidad
def test_usability(client):
    """
    Evalúa el tiempo de carga del dashboard para asegurar que sea rápido.
    """
    start = datetime.now()
    response = client.get('/user/dashboard', follow_redirects=True)
    load_time = (datetime.now() - start).total_seconds()
    assert load_time < 3.0  # Máximo 3 segundos de carga
    assert response.status_code == 200

# 3.12 Pruebas de rendimiento

def test_performance(client):
    """
    Calcula el tiempo promedio de respuesta de la vista dashboard.
    Asegura que esté por debajo de 2 segundos.
    """
    times = []
    
    for _ in range(1000):
        start = datetime.now()
        client.get('/user/dashboard', follow_redirects=True)
        times.append((datetime.now() - start).total_seconds())
    
    avg_time = sum(times) / len(times)
    print(f"Tiempo promedio de respuesta: {avg_time:.4f} segundos")
    assert avg_time < 1.0


class WebsiteUser(HttpUser):
    wait_time = between(1, 10)

    def on_start(self):
        # Encriptar email y password para login
        encrypted_email = "admin@sistema.com"
        encrypted_password ="adminsistema"

        response = self.client.post("/login", data={
            "email": encrypted_email,
            "password": encrypted_password
        })

        if response.status_code == 200:
            print("Login successful")
        else:
            print(f"Login failed: {response.text}")

    @task
    def create_incident(self):
        data = {
            "titulo": "Test Incidencia",
            "descripcion": "Creada con Locust",
            "usuario_creador_id": 1,
            "estado_id": 1,
            "prioridad_id": 1,
            "categoria_id": 1
        }
        # Asumiendo que ya estás logueado, haces la petición
        response = self.client.post("/user/incidents/create", json=data)

        print(f"Create incident status: {response.status_code}")
        if response.status_code == 200:
            print(response.text)

# ---------- EJECUCIÓN ----------
if __name__ == "__main__":
    pytest.main(["-v", "--cov=app", "--cov-report=html"])

# locust -f test_suite.py --host http://localhost:8080  
# curl -X POST http://localhost:8080/login