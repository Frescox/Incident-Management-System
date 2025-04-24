import mysql.connector
from flask import current_app

class Database:
    def __init__(self):
        self.connection = None

    def get_connection(self):
        """
        Obtiene una conexión a la base de datos
        """
        if self.connection is None or not self.connection.is_connected():
            try:
                self.connection = mysql.connector.connect(
                    host=current_app.config['DB_HOST'],
                    user=current_app.config['DB_USER'],
                    password=current_app.config['DB_PASSWORD'],
                    database=current_app.config['DB_NAME']
                )
            except mysql.connector.Error as e:
                current_app.logger.error(f"[DB ERROR] Conexión fallida: {e}")
                raise
        return self.connection

    def execute_query(self, query, params=None):
        """
        Ejecuta una consulta SQL
        
        Args:
            query (str): Consulta SQL a ejecutar
            params (tuple): Parámetros para la consulta
            
        Returns:
            El resultado de la consulta
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor(dictionary=True)

            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)

            result = cursor.fetchall()
            return result
        except mysql.connector.Error as e:
            current_app.logger.error(f"[DB ERROR] Consulta fallida: {e}")
            raise
        finally:
            try:
                cursor.close()
            except:
                pass

    def execute_non_query(self, query, params=None):
        """
        Ejecuta una consulta SQL que no devuelve resultados (INSERT, UPDATE, DELETE)
        
        Args:
            query (str): Consulta SQL a ejecutar
            params (tuple): Parámetros para la consulta
            
        Returns:
            El ID del último registro insertado o el número de filas afectadas
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)

            conn.commit()
            last_id = cursor.lastrowid
            affected_rows = cursor.rowcount
            return last_id if last_id else affected_rows
        except mysql.connector.Error as e:
            current_app.logger.error(f"[DB ERROR] Consulta no consultiva fallida: {e}")
            raise
        finally:
            try:
                cursor.close()
            except:
                pass

    def close(self):
        """
        Cierra la conexión con la base de datos
        """
        try:
            if self.connection and self.connection.is_connected():
                self.connection.close()
        except mysql.connector.Error as e:
            current_app.logger.error(f"[DB ERROR] Error al cerrar conexión: {e}")
        finally:
            self.connection = None

# Instancia global de Database
db = Database()