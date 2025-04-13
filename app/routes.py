from flask import Blueprint
from flask import jsonify
from app.models import Usuario

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    return "Bienvenido al sistema"

def init_app(app):
    app.register_blueprint(main_bp)