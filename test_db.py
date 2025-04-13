import sys
from pathlib import Path

# Asegura que Python encuentre los módulos
sys.path.append(str(Path(__file__).parent))

from app import create_app, db
from app.models import Usuario

app = create_app()

with app.app_context():
    try:
        db.engine.connect()
        print("¡Conexión exitosa a la base de datos!")
        print("Total de usuarios:", Usuario.query.count())
        print("\n".join([f"Nombre: {u.nombre} \nApellido: {u.apellido} \nEmail: {u.email} \n" for u in Usuario.query.all()]))

    except Exception as e:
        print("Error de conexión:", str(e))
        if "NoneType" in str(e):
            print("¿Has creado las tablas en la base de datos?")