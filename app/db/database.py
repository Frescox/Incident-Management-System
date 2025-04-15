import mysql.connector
from flask import current_app

class Database:
    def __init__(self):
        self.connection = None
    
    def get_connection(self):
        """
        Obtiene una conexión a la base de datos
        
        Returns:
            Una conexión activa a la base de datos MySQL
        """
        if self.connection is None or not self.connection.is_connected():
            self.connection = mysql.connector.connect(
                host=current_app.config['DB_HOST'],
                user=current_app.config['DB_USER'],
                password=current_app.config['DB_PASSWORD'],
                database=current_app.config['DB_NAME']
            )
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
        conn = self.get_connection()
        cursor = conn.cursor(dictionary=True)
        
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
            
        result = cursor.fetchall()
        cursor.close()
        
        return result
    
    def execute_non_query(self, query, params=None):
        """
        Ejecuta una consulta SQL que no devuelve resultados (INSERT, UPDATE, DELETE)
        
        Args:
            query (str): Consulta SQL a ejecutar
            params (tuple): Parámetros para la consulta
            
        Returns:
            El ID del último registro insertado o el número de filas afectadas
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
            
        conn.commit()
        last_id = cursor.lastrowid
        affected_rows = cursor.rowcount
        cursor.close()
        
        return last_id if last_id else affected_rows
    
    def close(self):
        """Cierra la conexión con la base de datos"""
        if self.connection:
            self.connection.close()
            self.connection = None

# Instancia global de Database
db = Database()