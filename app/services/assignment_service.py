from app.db.database import db
import random

class AssignmentService:
    def __init__(self):
        self.db = db

    def get_agents_by_category(self, categoria_id):
        """
        Devuelve una lista de agentes disponibles para una categoría específica.
        """
        query = """
            SELECT u.id, u.nombre, u.apellido
            FROM usuarios u
            WHERE u.rol_id = %s
              AND u.estado = 'activo'
        """
        # rol_id = 2 (agente)
        return self.db.execute_query(query, (2,))

    def get_last_assigned_agent(self, categoria_id):
        """
        Consulta al último agente asignado en esta categoría.
        """
        query = """
            SELECT i.agente_asignado_id
            FROM incidencias i
            JOIN categorias c ON i.categoria_id = c.id
            WHERE c.id = %s AND i.agente_asignado_id IS NOT NULL
            ORDER BY i.fecha_creacion DESC
            LIMIT 1
        """
        results = self.db.execute_query(query, (categoria_id,))
        return results[0]['agente_asignado_id'] if results else None

    def assign_agent(self, categoria_id):
        """
        Algoritmo de asignación rotativa simple.
        """
        agentes = self.get_agents_by_category(categoria_id)
        if not agentes:
            return None  # No hay agentes disponibles

        ultimo = self.get_last_assigned_agent(categoria_id)

        # Rotación: buscar el siguiente agente después del último asignado
        if ultimo:
            for i, agente in enumerate(agentes):
                if agente['id'] == ultimo:
                    siguiente_index = (i + 1) % len(agentes)
                    return agentes[siguiente_index]['id']
        
        # Si no hay historial, o no se encontró el último en la lista
        return agentes[0]['id']  # O random.choice(agentes)['id'] para aleatorio
