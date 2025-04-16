from flask import Blueprint
from app.controllers.auth_controller import AuthController
from app.controllers.user_controller import UserController
from app.controllers.agent_controller import AgentController

auth_bp = Blueprint('auth', __name__)
user_bp = Blueprint('user', __name__, url_prefix='/user')
agent_bp = Blueprint('agent', __name__, url_prefix='/agent')

# Auth Routes
auth_bp.route('/', methods=['GET'])(AuthController.index)
auth_bp.route('/register', methods=['POST'])(AuthController.register)
auth_bp.route('/verify_otp', methods=['POST'])(AuthController.verify_otp)
auth_bp.route('/login', methods=['POST'])(AuthController.login)
auth_bp.route('/logout', methods=['GET'])(AuthController.logout)

# User Routes
user_bp.route('/dashboard', methods=['GET'])(UserController.dashboard)
user_bp.route('/incidents/create', methods=['POST'])(UserController.create_incident)
user_bp.route('/incidents/<int:incident_id>', methods=['GET'])(UserController.view_incident)
user_bp.route('/incidents/<int:incident_id>/update', methods=['POST'])(UserController.update_incident)
user_bp.route('/incidents/<int:incident_id>/delete', methods=['POST'])(UserController.delete_incident)
user_bp.route('/incidents/<int:incident_id>/comments', methods=['POST'])(UserController.add_comment)

# Agent Routes
agent_bp.route('/dashboard', methods=['GET'])(AgentController.dashboard)
agent_bp.route('/incidents', methods=['GET'])(AgentController.list_incidents)
agent_bp.route('/incidents/<int:incident_id>', methods=['GET'])(AgentController.view_incident)
agent_bp.route('/incidents/<int:incident_id>/status', methods=['POST'])(AgentController.change_status)

def init_routes(app):
    app.register_blueprint(auth_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(agent_bp)