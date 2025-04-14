from flask import Blueprint
from app.controllers import incident_controller

main_routes = Blueprint('main', __name__)

@main_routes.route('/')
def home():
    return "Sistema de Gestión de Incidencias"