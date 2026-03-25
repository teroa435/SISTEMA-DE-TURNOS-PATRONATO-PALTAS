# conexion/conexion.py
import mysql.connector
from flask import g

class MySQLConnection:
    def __init__(self):
        self.host = '127.0.0.1'
        self.user = 'root'
        self.password = ''
        self.database = 'turnos_db'
        self.port = 3306
        self.connection = None
    
    def connect(self):
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database,
                port=self.port
            )
            print(f"Conectado a MySQL: {self.database}")
            return True
        except Exception as e:
            print(f"Error: {e}")
            return False
    
    def execute_query(self, query, params=None):
        cursor = self.connection.cursor(dictionary=True)
        try:
            cursor.execute(query, params or ())
            self.connection.commit()
            return cursor.rowcount
        finally:
            cursor.close()
    
    def fetch_all(self, query, params=None):
        cursor = self.connection.cursor(dictionary=True)
        try:
            cursor.execute(query, params or ())
            return cursor.fetchall()
        finally:
            cursor.close()
    
    def fetch_one(self, query, params=None):
        cursor = self.connection.cursor(dictionary=True)
        try:
            cursor.execute(query, params or ())
            return cursor.fetchone()
        finally:
            cursor.close()
    
    def close(self):
        if self.connection:
            self.connection.close()

def get_db():
    if 'db' not in g:
        g.db = MySQLConnection()
        g.db.connect()
    return g.db

def close_db(e=None):
    db = g.pop('db', None)
    if db:
        db.close()
