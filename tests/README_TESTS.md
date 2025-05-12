# Pruebas Unitarias para el Sistema de Gestión de Incidencias

Este directorio contiene las pruebas unitarias para validar el funcionamiento correcto de todos los componentes del sistema de gestión de incidencias.

## Estructura de las Pruebas

El conjunto de pruebas sigue la misma estructura del proyecto:

```
tests/
├── conftest.py            # Configuración y fixtures comunes para todas las pruebas
├── test_auth.py           # Pruebas para la autenticación
├── test_user_model.py     # Pruebas para el modelo de usuarios
├── test_ticket_models.py  # Pruebas para los modelos de incidencias y comentarios
├── test_catalog_models.py # Pruebas para los modelos de catálogo
├── test_user_controller.py      # Pruebas para el controlador de usuario
├── test_agent_controller.py     # Pruebas para el controlador de agente
├── test_admin_controller.py     # Pruebas para el controlador de administrador
├── test_services.py       # Pruebas para los servicios (mail, notificaciones, etc.)
└── test_utils.py          # Pruebas para las utilidades (encriptación, logging, etc.)
```

## Requisitos

Para ejecutar las pruebas, necesitarás las siguientes dependencias:

```
pytest
pytest-cov
pytest-mock
pytest-flask
coverage
```

Puedes instalarlas con:

```bash
pip install -r requirements-test.txt
```

## Ejecutar las Pruebas

### Ejecutar todas las pruebas

```bash
pytest
```

### Ejecutar con cobertura

```bash
pytest --cov=app
```

### Generar informe de cobertura HTML

```bash
pytest --cov=app --cov-report=html
```

Luego puedes abrir `htmlcov/index.html` en tu navegador para ver el informe detallado.

### Ejecutar pruebas específicas

```bash
# Ejecutar pruebas de un archivo específico
pytest tests/test_auth.py

# Ejecutar una prueba específica
pytest tests/test_auth.py::TestAuthController::test_login_success
```

## Configuración para Pruebas

Las pruebas utilizan una base de datos SQLite en memoria para proporcionar un entorno aislado y rápido. Esto se configura en `config.py` en la clase `TestingConfig`.

## Información Adicional

- Las pruebas utilizan "mocks" para simular componentes externos como el servicio de correo o SMS
- Se utilizan fixtures de pytest para configurar el entorno de prueba y crear datos de prueba
- Las pruebas están diseñadas para ser independientes entre sí y para limpiar después de su ejecución

## Mejores Prácticas

1. Mantén las pruebas independientes
2. Limpia después de cada prueba
3. Usa fixtures para la configuración común
4. Prueba tanto los casos de éxito como los de error
5. Mantén las pruebas rápidas y eficientes
6. Actualiza las pruebas cuando cambies la funcionalidad