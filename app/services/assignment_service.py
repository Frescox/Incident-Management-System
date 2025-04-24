from app.db.database import db
from app.utils.aes_encryption import decrypt
import random

class AssignmentService:
    def __init__(self):
        self.db = db

    def get_available_agents(self):
        """
        Devuelve agentes activos que no tienen ninguna incidencia asignada.
        """
        query = """
            SELECT u.id, u.nombre, u.apellido
            FROM usuarios u
            LEFT JOIN incidencias i ON u.id = i.agente_asignado_id
            WHERE u.rol_id = %s
            AND u.estado = 1
            AND i.id IS NULL
        """
        agentes = self.db.execute_query(query, (2,))

        for agente in agentes:
            try:
                agente['nombre'] = decrypt(agente['nombre']) if agente['nombre'] else ""
                agente['apellido'] = decrypt(agente['apellido']) if agente['apellido'] else ""
            except Exception as e:
                print(f"[ERROR] Falló la desencriptación de nombre o apellido: {e}")
                agente['nombre'] = "Desconocido"
                agente['apellido'] = ""

        return agentes
    
    def get_agent_with_least_incidents(self):
        """
        Devuelve el agente con menos incidencias asignadas.
        """
        query = """
            SELECT u.id, COUNT(i.id) AS num_incidencias
            FROM usuarios u
            LEFT JOIN incidencias i ON u.id = i.agente_asignado_id
            WHERE u.rol_id = %s
            AND u.estado = 1
            GROUP BY u.id
            ORDER BY num_incidencias ASC
            LIMIT 1
        """
        agentes = self.db.execute_query(query, (2,))
        return agentes[0]['id'] if agentes else None

    def assign_agent(self):
        """
        Asigna un agente activo disponible. Si todos tienen incidencias,
        asigna al agente con menos carga de incidencias.
        """
        agentes = self.get_available_agents()
        if agentes:
            return random.choice(agentes)['id']  # Asignas a un agente sin incidencias

        agente_id = self.get_agent_with_least_incidents()
        if agente_id:
            return agente_id  # Asignas al que tenga menos incidencias

        raise ValueError("No hay agentes disponibles.")