# decorators.py
# Decoradores para proteger rutas

from functools import wraps
from flask import flash, redirect, url_for
from flask_login import current_user

def login_required_message(message="Debe iniciar sesión para acceder a esta página"):
    """Decorador para requerir inicio de sesión con mensaje personalizado"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash(message, 'warning')
                return redirect(url_for('login'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def admin_required(message="Se requieren permisos de administrador"):
    """Decorador para requerir permisos de administrador"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash("Debe iniciar sesión", 'warning')
                return redirect(url_for('login'))
            # Aquí puedes agregar lógica para verificar si es admin
            # Por ejemplo, si tienes un campo 'rol' en la tabla usuarios
            # if current_user.rol != 'admin':
            #     flash(message, 'danger')
            #     return redirect(url_for('index'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator
