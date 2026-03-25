# user_model.py
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
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

def get_db():
    if 'db' not in g:
        g.db = MySQLConnection()
        g.db.connect()
    return g.db

def close_db(e=None):
    db = g.pop('db', None)
    if db:
        db.close()

class Usuario(UserMixin):
    def __init__(self, id_usuario, nombre, email, password):
        self.id = id_usuario
        self.nombre = nombre
        self.email = email
        self.password = password
    
    @staticmethod
    def get_by_id(user_id):
        try:
            db = get_db()
            result = db.fetch_one("SELECT * FROM usuarios WHERE id_usuario = %s", (user_id,))
            if result:
                return Usuario(result['id_usuario'], result['nombre'], result['mail'], result['password'])
            return None
        except Exception as e:
            print(f"Error: {e}")
            return None
    
    @staticmethod
    def get_by_email(email):
        try:
            db = get_db()
            result = db.fetch_one("SELECT * FROM usuarios WHERE mail = %s", (email,))
            if result:
                return Usuario(result['id_usuario'], result['nombre'], result['mail'], result['password'])
            return None
        except Exception as e:
            print(f"Error: {e}")
            return None
    
    @staticmethod
    def create(nombre, email, password):
        try:
            db = get_db()
            password_hash = generate_password_hash(password)
            query = "INSERT INTO usuarios (nombre, mail, password) VALUES (%s, %s, %s)"
            result = db.execute_query(query, (nombre, email, password_hash))
            if result > 0:
                return Usuario.get_by_email(email)
            return None
        except Exception as e:
            print(f"Error: {e}")
            return None
    
    def check_password(self, password):
        return check_password_hash(self.password, password)
