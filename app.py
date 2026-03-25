from flask import Flask, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import mysql.connector
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'clave-secreta-2024'

# Configurar Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Conexión a MySQL
def get_db():
    return mysql.connector.connect(
        host='127.0.0.1',
        user='root',
        password='',
        database='turnos_db'
    )

# Crear tablas si no existen
try:
    conn = get_db()
    cursor = conn.cursor()
    
    # Tabla de usuarios
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INT AUTO_INCREMENT PRIMARY KEY,
            nombre VARCHAR(100),
            email VARCHAR(100) UNIQUE,
            password VARCHAR(255)
        )
    ''')
    
    # Tabla de turnos
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS turnos (
            id INT AUTO_INCREMENT PRIMARY KEY,
            usuario_id INT,
            nombre_completo VARCHAR(100),
            cedula VARCHAR(20),
            telefono VARCHAR(20),
            servicio VARCHAR(50),
            fecha DATE,
            hora TIME,
            motivo TEXT,
            estado VARCHAR(20) DEFAULT "Programado",
            fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
        )
    ''')
    
    conn.commit()
    cursor.close()
    conn.close()
    print("Base de datos lista")
except Exception as e:
    print(f"Error: {e}")

# Modelo Usuario
class Usuario:
    def __init__(self, id, nombre, email, password):
        self.id = id
        self.nombre = nombre
        self.email = email
        self.password = password
    
    def is_authenticated(self):
        return True
    
    def is_active(self):
        return True
    
    def is_anonymous(self):
        return False
    
    def get_id(self):
        return str(self.id)

@login_manager.user_loader
def load_user(user_id):
    try:
        conn = get_db()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM usuarios WHERE id = %s", (user_id,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        if user:
            return Usuario(user['id'], user['nombre'], user['email'], user['password'])
    except:
        pass
    return None

# CSS Global
CSS = '''
<style>
    * {
        margin: 0;
        padding: 0;
        box-sizing: border-box;
    }
    
    body {
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        min-height: 100vh;
    }
    
    .nav-bar {
        background: white;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        padding: 15px 30px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    
    .nav-bar .brand {
        font-size: 20px;
        font-weight: bold;
        color: #667eea;
    }
    
    .nav-bar a {
        color: #667eea;
        text-decoration: none;
        margin-left: 20px;
    }
    
    .nav-bar a:hover {
        text-decoration: underline;
    }
    
    .container {
        background: white;
        border-radius: 20px;
        box-shadow: 0 20px 40px rgba(0,0,0,0.1);
        padding: 40px;
        width: 100%;
        max-width: 600px;
        margin: 40px auto;
        animation: fadeIn 0.5s ease-in;
    }
    
    .container-large {
        max-width: 1200px;
    }
    
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(-20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    h2 {
        text-align: center;
        color: #333;
        margin-bottom: 30px;
    }
    
    .form-group {
        margin-bottom: 20px;
    }
    
    label {
        display: block;
        margin-bottom: 8px;
        color: #555;
        font-weight: 500;
    }
    
    input, select, textarea {
        width: 100%;
        padding: 12px 15px;
        border: 2px solid #e0e0e0;
        border-radius: 10px;
        font-size: 16px;
        transition: all 0.3s;
        outline: none;
    }
    
    input:focus, select:focus, textarea:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    }
    
    button {
        width: 100%;
        padding: 12px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 10px;
        font-size: 16px;
        font-weight: bold;
        cursor: pointer;
        transition: transform 0.3s;
    }
    
    button:hover {
        transform: translateY(-2px);
    }
    
    .btn-secondary {
        background: #6c757d;
        margin-top: 10px;
    }
    
    .link {
        text-align: center;
        margin-top: 20px;
        padding-top: 20px;
        border-top: 1px solid #e0e0e0;
    }
    
    .link a {
        color: #667eea;
        text-decoration: none;
    }
    
    .message {
        padding: 12px;
        border-radius: 10px;
        margin-bottom: 20px;
        text-align: center;
    }
    
    .message.success { background: #d4edda; color: #155724; }
    .message.error { background: #f8d7da; color: #721c24; }
    
    table {
        width: 100%;
        border-collapse: collapse;
        margin-top: 20px;
    }
    
    th, td {
        padding: 12px;
        text-align: left;
        border-bottom: 1px solid #e0e0e0;
    }
    
    th {
        background: #f8f9fa;
        color: #333;
    }
    
    .badge {
        padding: 5px 10px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: bold;
    }
    
    .badge-programado { background: #ffc107; color: #333; }
    .badge-confirmado { background: #28a745; color: white; }
    .badge-cancelado { background: #dc3545; color: white; }
    
    .btn-sm {
        padding: 5px 10px;
        font-size: 12px;
        width: auto;
        margin: 0 5px;
        display: inline-block;
    }
    
    .card-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
        gap: 20px;
        margin-top: 20px;
    }
    
    .service-card {
        background: #f8f9fa;
        padding: 25px;
        border-radius: 15px;
        text-align: center;
        cursor: pointer;
        transition: all 0.3s;
    }
    
    .service-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 20px rgba(0,0,0,0.1);
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
    }
    
    .service-card h3 { margin-bottom: 10px; }
    .service-card p { font-size: 14px; }
    
    .row {
        display: flex;
        gap: 20px;
        margin-top: 20px;
    }
    
    .col {
        flex: 1;
    }
</style>
'''

# RUTAS PRINCIPALES
@app.route('/')
def index():
    return f'''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Patronato de Catacocha</title>
        {CSS}
    </head>
    <body>
        <div class="nav-bar">
            <span class="brand">🏛️ Patronato de Catacocha</span>
            <div>
                <a href="/">Inicio</a>
                <a href="/agendar">Agendar Turno</a>
                <a href="/mis-turnos">Mis Turnos</a>
                <a href="/perfil">Mi Perfil</a>
                <a href="/logout">Salir</a>
            </div>
        </div>
        <div class="container">
            <h2>🏛️ Sistema de Agendamiento de Turnos</h2>
            <p style="text-align: center; margin-bottom: 30px;">Bienvenido, {current_user.nombre if current_user.is_authenticated else "Visitante"}</p>
            <div class="card-grid">
                <a href="/agendar" style="text-decoration: none;">
                    <div class="service-card">
                        <h3>📅 Agendar Turno</h3>
                        <p>Solicita una cita médica</p>
                    </div>
                </a>
                <a href="/mis-turnos" style="text-decoration: none;">
                    <div class="service-card">
                        <h3>📋 Mis Turnos</h3>
                        <p>Consulta tus citas programadas</p>
                    </div>
                </a>
                <a href="/perfil" style="text-decoration: none;">
                    <div class="service-card">
                        <h3>👤 Mi Perfil</h3>
                        <p>Actualiza tu información</p>
                    </div>
                </a>
            </div>
        </div>
    </body>
    </html>
    '''

# AGENDAR TURNO
@app.route('/agendar', methods=['GET', 'POST'])
@login_required
def agendar_turno():
    if request.method == 'POST':
        try:
            datos = (
                current_user.id,
                request.form.get('nombre_completo'),
                request.form.get('cedula'),
                request.form.get('telefono'),
                request.form.get('servicio'),
                request.form.get('fecha'),
                request.form.get('hora'),
                request.form.get('motivo')
            )
            
            conn = get_db()
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO turnos (usuario_id, nombre_completo, cedula, telefono, servicio, fecha, hora, motivo)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ''', datos)
            conn.commit()
            cursor.close()
            conn.close()
            
            return f'''
            <!DOCTYPE html>
            <html>
            <head>
                <title>Turno Agendado</title>
                {CSS}
            </head>
            <body>
                <div class="nav-bar">
                    <span class="brand">🏛️ Patronato de Catacocha</span>
                    <div><a href="/">Inicio</a><a href="/mis-turnos">Mis Turnos</a><a href="/logout">Salir</a></div>
                </div>
                <div class="container">
                    <div class="message success">✅ ¡Turno agendado exitosamente!</div>
                    <div class="link"><a href="/mis-turnos">Ver mis turnos</a> | <a href="/">Volver al inicio</a></div>
                </div>
            </body>
            </html>
            '''
        except Exception as e:
            return f'''
            <!DOCTYPE html>
            <html>
            <head>
                <title>Error</title>
                {CSS}
            </head>
            <body>
                <div class="container">
                    <div class="message error">❌ Error: {e}</div>
                    <div class="link"><a href="/agendar">Volver a intentar</a></div>
                </div>
            </body>
            </html>
            '''
    
    return f'''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Agendar Turno</title>
        {CSS}
    </head>
    <body>
        <div class="nav-bar">
            <span class="brand">🏛️ Patronato de Catacocha</span>
            <div><a href="/">Inicio</a><a href="/mis-turnos">Mis Turnos</a><a href="/perfil">Mi Perfil</a><a href="/logout">Salir</a></div>
        </div>
        <div class="container">
            <h2>📅 Agendar Nuevo Turno</h2>
            <form method="POST">
                <div class="form-group">
                    <label>Nombre completo</label>
                    <input type="text" name="nombre_completo" value="{current_user.nombre}" required>
                </div>
                <div class="form-group">
                    <label>Cédula</label>
                    <input type="text" name="cedula" placeholder="Ingresa tu cédula" required>
                </div>
                <div class="form-group">
                    <label>Teléfono</label>
                    <input type="tel" name="telefono" placeholder="0991234567" required>
                </div>
                <div class="form-group">
                    <label>Servicio médico</label>
                    <select name="servicio" required>
                        <option value="">Selecciona un servicio</option>
                        <option value="Medicina General">🩺 Medicina General</option>
                        <option value="Pediatría">👶 Pediatría</option>
                        <option value="Ginecología">👩 Ginecología</option>
                        <option value="Odontología">🦷 Odontología</option>
                        <option value="Cardiología">❤️ Cardiología</option>
                        <option value="Trabajo Social">🤝 Trabajo Social</option>
                    </select>
                </div>
                <div class="row">
                    <div class="col">
                        <div class="form-group">
                            <label>Fecha</label>
                            <input type="date" name="fecha" required>
                        </div>
                    </div>
                    <div class="col">
                        <div class="form-group">
                            <label>Hora</label>
                            <input type="time" name="hora" required>
                        </div>
                    </div>
                </div>
                <div class="form-group">
                    <label>Motivo de consulta</label>
                    <textarea name="motivo" rows="3" placeholder="Describe el motivo de tu consulta"></textarea>
                </div>
                <button type="submit">Agendar Turno</button>
                <a href="/"><button type="button" class="btn-secondary">Cancelar</button></a>
            </form>
        </div>
    </body>
    </html>
    '''

# MIS TURNOS
@app.route('/mis-turnos')
@login_required
def mis_turnos():
    try:
        conn = get_db()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM turnos WHERE usuario_id = %s ORDER BY fecha DESC", (current_user.id,))
        turnos = cursor.fetchall()
        cursor.close()
        conn.close()
        
        if not turnos:
            turnos_html = '<p style="text-align: center;">No tienes turnos agendados. <a href="/agendar">Agendar turno</a></p>'
        else:
            turnos_html = '''
            <table>
                <thead>
                    <tr>
                        <th>Fecha</th>
                        <th>Hora</th>
                        <th>Servicio</th>
                        <th>Estado</th>
                        <th>Acciones</th>
                    </tr>
                </thead>
                <tbody>
            '''
            for t in turnos:
                estado_class = {
                    'Programado': 'badge-programado',
                    'Confirmado': 'badge-confirmado',
                    'Cancelado': 'badge-cancelado'
                }.get(t['estado'], 'badge-programado')
                
                turnos_html += f'''
                    <tr>
                        <td>{t['fecha']}</td>
                        <td>{t['hora']}</td>
                        <td>{t['servicio']}</td>
                        <td><span class="badge {estado_class}">{t['estado']}</span></td>
                        <td>
                            <a href="/cancelar-turno/{t['id']}" onclick="return confirm('¿Cancelar este turno?')">
                                <button class="btn-sm" style="background:#dc3545;color:white;">Cancelar</button>
                            </a>
                        </td>
                    </tr>
                '''
            turnos_html += '</tbody></table>'
        
        return f'''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Mis Turnos</title>
            {CSS}
        </head>
        <body>
            <div class="nav-bar">
                <span class="brand">🏛️ Patronato de Catacocha</span>
                <div><a href="/">Inicio</a><a href="/agendar">Agendar</a><a href="/perfil">Mi Perfil</a><a href="/logout">Salir</a></div>
            </div>
            <div class="container container-large">
                <h2>📋 Mis Turnos</h2>
                {turnos_html}
                <div class="link"><a href="/agendar">+ Agendar nuevo turno</a></div>
            </div>
        </body>
        </html>
        '''
    except Exception as e:
        return f'Error: {e}'

# CANCELAR TURNO
@app.route('/cancelar-turno/<int:id>')
@login_required
def cancelar_turno(id):
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("UPDATE turnos SET estado = 'Cancelado' WHERE id = %s AND usuario_id = %s", (id, current_user.id))
        conn.commit()
        cursor.close()
        conn.close()
        return redirect(url_for('mis_turnos'))
    except Exception as e:
        return f'Error: {e}'

# PERFIL
@app.route('/perfil')
@login_required
def perfil():
    return f'''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Mi Perfil</title>
        {CSS}
    </head>
    <body>
        <div class="nav-bar">
            <span class="brand">🏛️ Patronato de Catacocha</span>
            <div><a href="/">Inicio</a><a href="/agendar">Agendar</a><a href="/mis-turnos">Mis Turnos</a><a href="/logout">Salir</a></div>
        </div>
        <div class="container">
            <h2>👤 Mi Perfil</h2>
            <p><strong>Nombre:</strong> {current_user.nombre}</p>
            <p><strong>Email:</strong> {current_user.email}</p>
            <div class="link"><a href="/agendar">Agendar turno</a> | <a href="/mis-turnos">Ver mis turnos</a></div>
        </div>
    </body>
    </html>
    '''

# REGISTRO
@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm = request.form.get('confirm_password')
        
        if password != confirm:
            return f'''
            <!DOCTYPE html>
            <html>
            <head><title>Error</title>{CSS}</head>
            <body><div class="container"><div class="message error">❌ Las contraseñas no coinciden</div><div class="link"><a href="/registro">Volver</a></div></div></body>
            </html>
            '''
        
        password_hash = generate_password_hash(password)
        try:
            conn = get_db()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO usuarios (nombre, email, password) VALUES (%s, %s, %s)", (nombre, email, password_hash))
            conn.commit()
            cursor.close()
            conn.close()
            return f'''
            <!DOCTYPE html>
            <html>
            <head><title>Registro Exitoso</title>{CSS}</head>
            <body><div class="container"><div class="message success">✅ Registro exitoso!</div><div class="link"><a href="/login">Iniciar Sesión</a></div></div></body>
            </html>
            '''
        except Exception as e:
            return f'''
            <!DOCTYPE html>
            <html>
            <head><title>Error</title>{CSS}</head>
            <body><div class="container"><div class="message error">❌ Error: {e}</div><div class="link"><a href="/registro">Volver</a></div></div></body>
            </html>
            '''
    
    return f'''
    <!DOCTYPE html>
    <html>
    <head><title>Registro</title>{CSS}</head>
    <body>
        <div class="container">
            <h2>📝 Registro de Usuario</h2>
            <form method="POST">
                <div class="form-group"><label>Nombre completo</label><input type="text" name="nombre" required></div>
                <div class="form-group"><label>Email</label><input type="email" name="email" required></div>
                <div class="form-group"><label>Contraseña</label><input type="password" name="password" required></div>
                <div class="form-group"><label>Confirmar contraseña</label><input type="password" name="confirm_password" required></div>
                <button type="submit">Registrarse</button>
            </form>
            <div class="link">¿Ya tienes cuenta? <a href="/login">Inicia sesión aquí</a></div>
        </div>
    </body>
    </html>
    '''

# LOGIN
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        try:
            conn = get_db()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM usuarios WHERE email = %s", (email,))
            user = cursor.fetchone()
            cursor.close()
            conn.close()
            if user and check_password_hash(user['password'], password):
                usuario = Usuario(user['id'], user['nombre'], user['email'], user['password'])
                login_user(usuario)
                return redirect(url_for('index'))
            return f'''
            <!DOCTYPE html>
            <html>
            <head><title>Error</title>{CSS}</head>
            <body><div class="container"><div class="message error">❌ Credenciales incorrectas</div><div class="link"><a href="/login">Volver</a></div></div></body>
            </html>
            '''
        except Exception as e:
            return f'Error: {e}'
    
    return f'''
    <!DOCTYPE html>
    <html>
    <head><title>Login</title>{CSS}</head>
    <body>
        <div class="container">
            <h2>🔐 Iniciar Sesión</h2>
            <form method="POST">
                <div class="form-group"><label>Email</label><input type="email" name="email" required></div>
                <div class="form-group"><label>Contraseña</label><input type="password" name="password" required></div>
                <button type="submit">Ingresar</button>
            </form>
            <div class="link">¿No tienes cuenta? <a href="/registro">Regístrate aquí</a></div>
        </div>
    </body>
    </html>
    '''

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return f'''
    <!DOCTYPE html>
    <html>
    <head><title>Sesión Cerrada</title>{CSS}</head>
    <body><div class="container"><div class="message success">✅ Sesión cerrada correctamente</div><div class="link"><a href="/">Volver al inicio</a></div></div></body>
    </html>
    '''

if __name__ == '__main__':
    app.run(debug=True)
