from app.models.core import db
from app.models.user_rol_models import Usuario
from app.models.ticket_models import Incidencia
from app.utils.aes_encryption import decrypt
import random
from sqlalchemy import func


class AssignmentService:
    def __init__(self):
        self.db = db

    def get_available_agents(self):
        """
        Devuelve agentes activos que no tienen ninguna incidencia asignada.
        """
        agentes = (
            self.db.session.query(Usuario)
            .outerjoin(Incidencia, Usuario.id == Incidencia.agente_asignado_id)
            .filter(
                Usuario.rol_id == 2,
                Usuario.estado == 1,
                Incidencia.id == None  # Ninguna incidencia asignada
            )
            .all()
        )

        resultado = []
        for agente in agentes:
            try:
                nombre = decrypt(agente.nombre) if agente.nombre else "Desconocido"
                apellido = decrypt(agente.apellido) if agente.apellido else ""
            except Exception as e:
                print(f"[ERROR] Falló la desencriptación de nombre o apellido: {e}")
                nombre = "Desconocido"
                apellido = ""

            resultado.append({
                "id": agente.id,
                "nombre": nombre,
                "apellido": apellido
            })

        return resultado

    def get_agent_with_least_incidents(self):
        """
        Devuelve el agente con menos incidencias asignadas.
        """
        subquery = (
            self.db.session.query(
                Usuario.id.label('id'),
                func.count(Incidencia.id).label('num_incidencias')
            )
            .outerjoin(Incidencia, Usuario.id == Incidencia.agente_asignado_id)
            .filter(
                Usuario.rol_id == 2,
                Usuario.estado == 1
            )
            .group_by(Usuario.id)
            .order_by(func.count(Incidencia.id).asc())
            .limit(1)
            .first()
        )

        return subquery.id if subquery else None

    def assign_agent(self):
        """
        Asigna un agente activo disponible. Si todos tienen incidencias,
        asigna al agente con menos carga de incidencias.
        """
        agentes_disponibles = self.get_available_agents()
        if agentes_disponibles:
            return random.choice(agentes_disponibles)['id']

        agente_id = self.get_agent_with_least_incidents()
        if agente_id:
            return agente_id

        raise ValueError("No hay agentes disponibles.")
