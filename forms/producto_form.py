# forms/producto_form.py
# Formulario para productos

from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, IntegerField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length, NumberRange

class ProductoForm(FlaskForm):
    """Formulario para crear/editar productos"""
    nombre = StringField("Nombre", validators=[
        DataRequired(message="El nombre es requerido"),
        Length(min=2, max=100, message="El nombre debe tener entre 2 y 100 caracteres")
    ])
    precio = FloatField("Precio", validators=[
        DataRequired(message="El precio es requerido"),
        NumberRange(min=0, message="El precio debe ser mayor o igual a 0")
    ])
    stock = IntegerField("Stock", validators=[
        DataRequired(message="El stock es requerido"),
        NumberRange(min=0, message="El stock debe ser mayor o igual a 0")
    ])
    descripcion = TextAreaField("Descripcion", validators=[
        Length(max=500, message="La descripcion no puede exceder 500 caracteres")
    ])
    submit = SubmitField("Guardar")
