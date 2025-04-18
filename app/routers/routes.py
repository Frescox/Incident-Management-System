from flask import Blueprint
from app.controllers.auth_controller import AuthController
from app.controllers.user_controller import UserController
from app.controllers.agent_controller import AgentController
from app.controllers.admin_controller import AdminController

auth_bp = Blueprint('auth', __name__)
user_bp = Blueprint('user', __name__, url_prefix='/user')
agent_bp = Blueprint('agent', __name__, url_prefix='/agent')
admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

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
agent_bp.route('/incidents/list')(AgentController.list_incidents)
agent_bp.route('/incidents/view/<int:incident_id>')(AgentController.view_incident)
agent_bp.route('/incidents/update/<int:incident_id>', methods=['POST'])(AgentController.update_incident)
agent_bp.route('/incidents/assign/<int:incident_id>', methods=['POST'])(AgentController.assign_incident)
agent_bp.route('/incidents/change-status/<int:incident_id>', methods=['POST'])(AgentController.change_status)
agent_bp.route('/incidents/resolve/<int:incident_id>', methods=['POST'])(AgentController.resolve_incident)

# Admin Routes
admin_bp.route('/dashboard', methods=['GET'])(AdminController.dashboard)
admin_bp.route('/incidents/<int:incident_id>', methods=['GET'])(AdminController.view_incident)
admin_bp.route('/users/<int:user_id>/update_role', methods=['POST'])(AdminController.update_user_role)
admin_bp.route('/users/<int:user_id>/toggle_status', methods=['POST'])(AdminController.toggle_user_status)

def init_routes(app):
    app.register_blueprint(auth_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(agent_bp)
    app.register_blueprint(admin_bp)