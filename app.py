from flask import Flask, render_template

app = Flask(__name__)

# Ruta principal
@app.route('/')
def index():
    return render_template('index.html')

# Ruta dinámica para citas
@app.route('/cita/<paciente>')
def cita(paciente):
    mensaje = f"Bienvenido/a {paciente}, su cita en el Patronato del Cantón Paltas ha sido agendada exitosamente."
    return render_template('usuario.html', paciente=paciente, mensaje=mensaje)

# Ruta adicional para información de servicios
@app.route('/servicios')
def servicios():
    servicios_lista = [
        "Atención médica general",
        "Odontología",
        "Psicología",
        "Nutrición",
        "Asesoría legal"
    ]
    return render_template('servicios.html', servicios=servicios_lista)

if __name__ == '__main__':
    app.run(debug=True)