from flask import Flask, render_template
from datetime import datetime

app = Flask(__name__)

# Ruta principal - Página de inicio
@app.route('/')
def index():
    return render_template('index.html')

# Ruta dinámica para citas
@app.route('/cita/<paciente>')
def cita(paciente):
    fecha_actual = datetime.now().strftime("%d/%m/%Y")
    return render_template('cita.html', paciente=paciente, fecha=fecha_actual)

# Ruta para servicios
@app.route('/servicios')
def servicios():
    return render_template('servicios.html')

# Ruta para listado de citas
@app.route('/citas')
def citas():
    # Simulación de citas (luego vendrán de base de datos)
    citas_ejemplo = [
        {'paciente': 'María González', 'fecha': '15/03/2024', 'servicio': 'Medicina General'},
        {'paciente': 'Juan Pérez', 'fecha': '16/03/2024', 'servicio': 'Odontología'},
        {'paciente': 'Ana Rodríguez', 'fecha': '17/03/2024', 'servicio': 'Trabajo Social'}
    ]
    return render_template('citas.html', citas=citas_ejemplo)

# Ruta para contacto
@app.route('/contacto')
def contacto():
    return render_template('contacto.html')

# Ruta para acerca de
@app.route('/about')
def about():
    return render_template('about.html')

if __name__ == '__main__':
    app.run(debug=True)