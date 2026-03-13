# Conexion/conexion.py
# Configuración de conexión a MySQL para Flask

import mysql.connector
from mysql.connector import Error
from flask import current_app, g

class MySQLConnection:
    """Clase para manejar la conexión a MySQL"""
    
    def __init__(self, host='localhost', user='root', password='', database='turnos_db'):
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.connection = None
        self.cursor = None
    
    def connect(self):
        """Establece la conexión con MySQL"""
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database
            )
            
            if self.connection.is_connected():
                print(f"✅ Conectado a MySQL - Base de datos: {self.database}")
                return True
        except Error as e:
            print(f"❌ Error conectando a MySQL: {e}")
            return False
    
    def get_cursor(self, dictionary=True):
        """Obtiene un cursor para ejecutar consultas"""
        if not self.connection or not self.connection.is_connected():
            self.connect()
        
        # Si dictionary=True, los resultados serán diccionarios
        self.cursor = self.connection.cursor(dictionary=dictionary)
        return self.cursor
    
    def execute_query(self, query, params=None):
        """Ejecuta una consulta (INSERT, UPDATE, DELETE)"""
        cursor = self.get_cursor()
        try:
            cursor.execute(query, params or ())
            self.connection.commit()
            return cursor.rowcount
        except Error as e:
            print(f"❌ Error ejecutando consulta: {e}")
            self.connection.rollback()
            return -1
        finally:
            cursor.close()
    
    def fetch_all(self, query, params=None):
        """Ejecuta una consulta y retorna todos los resultados"""
        cursor = self.get_cursor()
        try:
            cursor.execute(query, params or ())
            return cursor.fetchall()
        except Error as e:
            print(f"❌ Error obteniendo datos: {e}")
            return []
        finally:
            cursor.close()
    
    def fetch_one(self, query, params=None):
        """Ejecuta una consulta y retorna un solo resultado"""
        cursor = self.get_cursor()
        try:
            cursor.execute(query, params or ())
            return cursor.fetchone()
        except Error as e:
            print(f"❌ Error obteniendo dato: {e}")
            return None
        finally:
            cursor.close()
    
    def close(self):
        """Cierra la conexión"""
        if self.cursor:
            self.cursor.close()
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("🔌 Conexión a MySQL cerrada")

# Configuración para usar en Flask
def get_db():
    """Obtiene la conexión a la base de datos (para usar con g)"""
    if 'db' not in g:
        g.db = MySQLConnection(
            host='localhost',      # Cambia si es necesario
            user='root',            # Tu usuario de MySQL
            password='',            # Tu contraseña de MySQL (vacía en XAMPP)
            database='turnos_db'    # Base de datos a usar
        )
        g.db.connect()
    return g.db

def close_db(e=None):
    """Cierra la conexión al final de la petición"""
    db = g.pop('db', None)
    if db is not None:
        db.close()

# Configuración usando variables de entorno (para producción)
import os

def get_db_from_env():
    """Obtiene configuración desde variables de entorno"""
    return MySQLConnection(
        host=os.environ.get('MYSQL_HOST', 'localhost'),
        user=os.environ.get('MYSQL_USER', 'root'),
        password=os.environ.get('MYSQL_PASSWORD', ''),
        database=os.environ.get('MYSQL_DATABASE', 'turnos_db')
    )
