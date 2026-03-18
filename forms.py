# forms.py
# Formularios para autenticación de usuarios

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError
from models import Usuario

class RegistroForm(FlaskForm):
    """Formulario de registro de usuarios"""
    nombre = StringField('Nombre completo', validators=[
        DataRequired(message='El nombre es requerido'),
        Length(min=2, max=100, message='El nombre debe tener entre 2 y 100 caracteres')
    ])
    
    email = StringField('Email', validators=[
        DataRequired(message='El email es requerido'),
        Email(message='Ingrese un email válido')
    ])
    
    password = PasswordField('Contraseña', validators=[
        DataRequired(message='La contraseña es requerida'),
        Length(min=6, message='La contraseña debe tener al menos 6 caracteres')
    ])
    
    confirm_password = PasswordField('Confirmar contraseña', validators=[
        DataRequired(message='Debe confirmar la contraseña'),
        EqualTo('password', message='Las contraseñas no coinciden')
    ])
    
    submit = SubmitField('Registrarse')
    
    def validate_email(self, email):
        """Verifica que el email no esté registrado"""
        usuario = Usuario.get_by_email(email.data)
        if usuario:
            raise ValidationError('Este email ya está registrado. Por favor, use otro.')

class LoginForm(FlaskForm):
    """Formulario de inicio de sesión"""
    email = StringField('Email', validators=[
        DataRequired(message='El email es requerido'),
        Email(message='Ingrese un email válido')
    ])
    
    password = PasswordField('Contraseña', validators=[
        DataRequired(message='La contraseña es requerida')
    ])
    
    submit = SubmitField('Iniciar Sesión')