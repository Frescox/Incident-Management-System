import sys
from pathlib import Path
import logging
from typing import List, Optional
from sqlalchemy import inspect, text
from sqlalchemy.exc import SQLAlchemyError

# Configuración inicial
def setup():
    # Configurar path
    project_root = Path(__file__).parent.parent
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
    
    # Configurar logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[logging.StreamHandler()]
    )
    return logging.getLogger('db_checker')

logger = setup()

try:
    from app import create_app, db
    from app.models.user_models import Usuario
except ImportError as e:
    logger.critical(f"Error de importación: {str(e)}")
    sys.exit(1)

class DatabaseChecker:
    def __init__(self):
        self.app = create_app()
        
    def check_connection(self) -> bool:
        """Verifica la conexión a la base de datos"""
        try:
            with self.app.app_context():
                with db.engine.connect() as conn:
                    conn.execute(text("SELECT 1"))  # Query de prueba
                logger.info("Conexión a la base de datos exitosa")
                return True
        except SQLAlchemyError as e:
            logger.error(f"Error de conexión: {str(e)}")
            return False
    
    def verify_tables(self) -> bool:
        """Verifica que las tablas requeridas existan"""
        required_tables = ['usuarios', 'roles']
        try:
            with self.app.app_context():
                inspector = inspect(db.engine)
                existing_tables = inspector.get_table_names()
                
                for table in required_tables:
                    if table not in existing_tables:
                        logger.error(f"Tabla faltante: {table}")
                        return False
                return True
        except Exception as e:
            logger.error(f"Error verificando tablas: {str(e)}")
            return False
    
    def get_users(self) -> Optional[List[Usuario]]:
        """Obtiene todos los usuarios de la base de datos"""
        try:
            with self.app.app_context():
                return Usuario.query.order_by(Usuario.id).all()
        except Exception as e:
            logger.error(f"Error obteniendo usuarios: {str(e)}")
            return None
    
    @staticmethod
    def format_user(user: Usuario) -> str:
        """Formatea la información del usuario para imprimir"""
        return (
            f"ID: {user.id}\n"
            f"Nombre: {user.nombre}\n"
            f"Apellido: {user.apellido}\n"
            f"Email: {user.email}\n"
            f"Rol ID: {user.rol_id}\n"
            "━━━━━━━━━━━━━━━━━━━━━━"
        )

def main():
    logger.info("Iniciando verificación de base de datos...")
    
    checker = DatabaseChecker()
    
    # 1. Verificar conexión
    if not checker.check_connection():
        sys.exit(1)
    
    # 2. Verificar tablas
    if not checker.verify_tables():
        sys.exit(1)
    
    # 3. Obtener y mostrar usuarios
    users = checker.get_users()
    
    if not users:
        logger.info("No hay usuarios registrados")
        return
    
    logger.info(f"Total de usuarios: {len(users)}")
    logger.info("👥 Lista de usuarios:")
    
    for user in users:
        logger.info(checker.format_user(user))

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        logger.critical(f"Error crítico: {str(e)}", exc_info=True)
        sys.exit(1)