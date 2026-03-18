# models.py
# Modelos para el Sistema de Turnos con Flask-Login

from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from Conexion.conexion import get_db

class Usuario(UserMixin):
    """Modelo de Usuario para Flask-Login con MySQL"""
    
    def __init__(self, id_usuario, nombre, email, password):
        self.id = id_usuario
        self.nombre = nombre
        self.email = email
        self.password = password
    
    @staticmethod
    def get_by_id(user_id):
        """Obtiene un usuario por su ID"""
        try:
            db = get_db()
            result = db.fetch_one("SELECT * FROM usuarios WHERE id_usuario = %s", (user_id,))
            if result:
                return Usuario(
                    id_usuario=result['id_usuario'],
                    nombre=result['nombre'],
                    email=result['mail'],
                    password=result['password']
                )
            return None
        except Exception as e:
            print(f"Error en get_by_id: {e}")
            return None
    
    @staticmethod
    def get_by_email(email):
        """Obtiene un usuario por su email"""
        try:
            db = get_db()
            result = db.fetch_one("SELECT * FROM usuarios WHERE mail = %s", (email,))
            if result:
                return Usuario(
                    id_usuario=result['id_usuario'],
                    nombre=result['nombre'],
                    email=result['mail'],
                    password=result['password']
                )
            return None
        except Exception as e:
            print(f"Error en get_by_email: {e}")
            return None
    
    @staticmethod
    def create(nombre, email, password):
        """Crea un nuevo usuario en la base de datos"""
        try:
            db = get_db()
            # Encriptar contraseña
            password_hash = generate_password_hash(password)
            
            query = "INSERT INTO usuarios (nombre, mail, password) VALUES (%s, %s, %s)"
            result = db.execute_query(query, (nombre, email, password_hash))
            
            if result > 0:
                # Obtener el ID del nuevo usuario
                usuario = db.fetch_one("SELECT * FROM usuarios WHERE mail = %s", (email,))
                if usuario:
                    return Usuario(
                        id_usuario=usuario['id_usuario'],
                        nombre=usuario['nombre'],
                        email=usuario['mail'],
                        password=usuario['password']
                    )
            return None
        except Exception as e:
            print(f"Error en create: {e}")
            return None
    
    def check_password(self, password):
        """Verifica si la contraseña es correcta"""
        return check_password_hash(self.password, password)
    
    @staticmethod
    def update_password(user_id, new_password):
        """Actualiza la contraseña de un usuario"""
        try:
            db = get_db()
            password_hash = generate_password_hash(new_password)
            query = "UPDATE usuarios SET password = %s WHERE id_usuario = %s"
            return db.execute_query(query, (password_hash, user_id))
        except Exception as e:
            print(f"Error en update_password: {e}")
            return -1