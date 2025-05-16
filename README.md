# Incident Management System

Sistema de gestión de incidencias desarrollado con Flask y MySQL (XAMPP).

## Requisitos previos

- [XAMPP](https://www.apachefriends.org/es/download.html) (con MySQL y Apache)
- [Python 3.9+](https://www.python.org/downloads/)
- `pip` (incluido con Python)

## Instalación

1. **Clona el repositorio**:
   ```bash
   git clone https://github.com/Frescox/Incident-Management-System.git
   cd Incident-Management-System
   ```

2. **Crea un ambiente virtual**:
   ```bash
   python -m venv venv
   .\venv\Scripts\activate
   ```

3. **Instala dependencias**:
   ```bash
   pip install -r requirements.txt
   ```

## Configuración de la base de datos (XAMPP)

### Inicia XAMPP:

- Ejecuta el panel de control de XAMPP  
- Inicia los módulos **Apache** y **MySQL**

### Crea la base de datos:

1. Abre [phpMyAdmin](http://localhost/phpmyadmin)  
2. Ejecuta el siguiente SQL:
   ```sql
   CREATE DATABASE sistema_incidencias;
   ```
3. Importa la base de datos existente: `app/db/incident_management_db.sql`

### Configura la conexión (opcional):

Si necesitas cambiar credenciales, edita `config.py`:

```python
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://usuario:contraseña@localhost/sistema_incidencias'
```

## 🏃 Ejecutar la aplicación

```bash
python run.py
```

Luego accede en tu navegador:

```
http://localhost:8080
```
o de esta otra:

```
http://127.0.0.1:8080
```

### Ejecutar las pruebas

```
pytest test_suite.py -v
```

# Credenciales para el admin

## Correo: admin@sistema.com

## passd:  adminsistema