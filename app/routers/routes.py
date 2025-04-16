from flask import Blueprint
from app.controllers.auth_controller import AuthController
from app.controllers.user_controller import UserController
from app.controllers.agent_controller import AgentController

# Crear blueprint para rutas de autenticación
auth_bp = Blueprint('auth', __name__)
# Crear blueprint con prefijos para evitar conflictos
user_bp = Blueprint('user', __name__, url_prefix='/user')
agent_bp = Blueprint('agent', __name__, url_prefix='/agent')


# Rutas de autenticación
auth_bp.route('/', methods=['GET'])(AuthController.index)
auth_bp.route('/register', methods=['POST'])(AuthController.register)
auth_bp.route('/verify_otp', methods=['POST'])(AuthController.verify_otp)
auth_bp.route('/login', methods=['POST'])(AuthController.login)
auth_bp.route('/logout')(AuthController.logout)
user_bp.route('/dashboard', methods=['GET'])(UserController.dashboard)
agent_bp.route('/dashboard', methods=['GET'])(AgentController.dashboard)

def init_routes(app):
    """
    Inicializa todas las rutas en la aplicación Flask
    
    Args:
        app: La aplicación Flask
    """
    # Rutas del usuario, agente y auth
    app.register_blueprint(auth_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(agent_bp) 