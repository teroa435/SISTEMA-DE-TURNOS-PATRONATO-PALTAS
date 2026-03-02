# form.py
# Formularios para la aplicación Flask

from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, IntegerField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length, Optional

class ProductoForm(FlaskForm):
    '''Formulario para productos'''
    nombre = StringField('Nombre', validators=[DataRequired(), Length(min=2, max=100)])
    descripcion = TextAreaField('Descripción', validators=[Optional(), Length(max=200)])
    precio = FloatField('Precio', validators=[DataRequired()])
    cantidad = IntegerField('Cantidad', validators=[DataRequired()])
    submit = SubmitField('Guardar')

class TurnoForm(FlaskForm):
    '''Formulario para turnos'''
    paciente = StringField('Nombre del Paciente', validators=[DataRequired(), Length(min=2, max=100)])
    cedula = StringField('Cédula', validators=[DataRequired(), Length(min=10, max=10)])
    fecha = StringField('Fecha (YYYY-MM-DD)', validators=[DataRequired()])
    hora = StringField('Hora (HH:MM)', validators=[DataRequired()])
    motivo = TextAreaField('Motivo de la consulta', validators=[Optional()])
    submit = SubmitField('Agendar Turno')
