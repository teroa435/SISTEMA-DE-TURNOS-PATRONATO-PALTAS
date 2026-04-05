from flask import Flask, request, redirect, url_for, flash, render_template_string
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import mysql.connector
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'clave-secreta-patronato-2024'

# ============================================
# CONFIGURACIÓN FLASK-LOGIN
# ============================================
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# ============================================
# CONEXIÓN A MYSQL
# ============================================
def get_db():
    return mysql.connector.connect(
        host='127.0.0.1',
        user='root',
        password='',
        database='turnos_db',
        port=3306
    )

# ============================================
# CREAR TABLAS (EJECUTAR AL INICIO)
# ============================================
def init_db():
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        # Tabla de usuarios
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS usuarios (
                id INT AUTO_INCREMENT PRIMARY KEY,
                nombre VARCHAR(100) NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL,
                password VARCHAR(255) NOT NULL,
                fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabla de servicios médicos
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS servicios (
                id INT AUTO_INCREMENT PRIMARY KEY,
                nombre VARCHAR(50) NOT NULL,
                descripcion TEXT,
                duracion INT DEFAULT 30
            )
        ''')
        
        # Tabla de turnos
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS turnos (
                id INT AUTO_INCREMENT PRIMARY KEY,
                usuario_id INT NOT NULL,
                nombre_completo VARCHAR(100) NOT NULL,
                cedula VARCHAR(20) NOT NULL,
                telefono VARCHAR(20) NOT NULL,
                servicio_id INT NOT NULL,
                servicio_nombre VARCHAR(50) NOT NULL,
                fecha DATE NOT NULL,
                hora TIME NOT NULL,
                motivo TEXT,
                estado VARCHAR(20) DEFAULT 'Programado',
                fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE,
                FOREIGN KEY (servicio_id) REFERENCES servicios(id) ON DELETE CASCADE
            )
        ''')
        
        # Insertar servicios por defecto si no existen
        cursor.execute("SELECT COUNT(*) FROM servicios")
        if cursor.fetchone()[0] == 0:
            servicios = [
                ('Medicina General', 'Atención médica general para todas las edades', 30),
                ('Pediatría', 'Atención especializada para niños y adolescentes', 30),
                ('Ginecología', 'Salud de la mujer y control prenatal', 30),
                ('Odontología', 'Cuidado dental y prevención', 30),
                ('Cardiología', 'Atención cardíaca especializada', 45),
                ('Trabajo Social', 'Asesoría familiar y gestión social', 30),
                ('Psicología', 'Apoyo emocional y salud mental', 45),
                ('Nutrición', 'Consejería nutricional', 30)
            ]
            cursor.executemany("INSERT INTO servicios (nombre, descripcion, duracion) VALUES (%s, %s, %s)", servicios)
        
        conn.commit()
        cursor.close()
        conn.close()
        print("✅ Base de datos inicializada correctamente")
    except Exception as e:
        print(f"⚠️ Error en base de datos: {e}")

init_db()

# ============================================
# MODELO USUARIO
# ============================================
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

# ============================================
# CSS GLOBAL
# ============================================
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
        flex-wrap: wrap;
    }
    
    .nav-bar .brand {
        font-size: 20px;
        font-weight: bold;
        color: #667eea;
    }
    
    .nav-bar .brand i {
        margin-right: 10px;
    }
    
    .nav-bar a {
        color: #667eea;
        text-decoration: none;
        margin-left: 20px;
        transition: 0.3s;
    }
    
    .nav-bar a:hover {
        color: #764ba2;
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
        font-family: inherit;
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
        transition: transform 0.3s, box-shadow 0.3s;
    }
    
    button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
    }
    
    .btn-secondary {
        background: #6c757d;
        margin-top: 10px;
    }
    
    .btn-secondary:hover {
        background: #5a6268;
        box-shadow: 0 5px 15px rgba(108, 117, 125, 0.4);
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
    
    .link a:hover {
        text-decoration: underline;
    }
    
    .message {
        padding: 12px;
        border-radius: 10px;
        margin-bottom: 20px;
        text-align: center;
    }
    
    .message.success { background: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
    .message.error { background: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }
    .message.info { background: #d1ecf1; color: #0c5460; border: 1px solid #bee5eb; }
    
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
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        font-weight: 600;
    }
    
    tr:hover {
        background: #f8f9fa;
    }
    
    .badge {
        padding: 5px 12px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: bold;
        display: inline-block;
    }
    
    .badge-programado { background: #ffc107; color: #333; }
    .badge-confirmado { background: #28a745; color: white; }
    .badge-cancelado { background: #dc3545; color: white; }
    .badge-completado { background: #6c757d; color: white; }
    
    .btn-sm {
        padding: 5px 12px;
        font-size: 12px;
        width: auto;
        margin: 0 5px;
        display: inline-block;
    }
    
    .btn-edit { background: #ffc107; color: #333; }
    .btn-delete { background: #dc3545; color: white; }
    .btn-view { background: #17a2b8; color: white; }
    
    .card-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
        gap: 20px;
        margin-top: 20px;
    }
    
    .service-card {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        padding: 25px;
        border-radius: 15px;
        text-align: center;
        cursor: pointer;
        transition: all 0.3s;
        text-decoration: none;
        color: inherit;
        display: block;
    }
    
    .service-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 25px rgba(0,0,0,0.15);
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
    }
    
    .service-card h3 { margin-bottom: 10px; font-size: 1.3rem; }
    .service-card p { font-size: 14px; opacity: 0.8; }
    
    .stats-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 20px;
        margin-bottom: 30px;
    }
    
    .stat-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 20px;
        border-radius: 15px;
        text-align: center;
    }
    
    .stat-card h3 { font-size: 2rem; margin-bottom: 5px; }
    .stat-card p { margin: 0; opacity: 0.9; }
    
    .row {
        display: flex;
        gap: 20px;
        flex-wrap: wrap;
    }
    
    .col {
        flex: 1;
        min-width: 200px;
    }
    
    .footer {
        text-align: center;
        padding: 20px;
        color: white;
        margin-top: 40px;
    }
    
    @media (max-width: 768px) {
        .container { margin: 20px; padding: 20px; }
        .nav-bar { flex-direction: column; gap: 10px; }
        .nav-bar div { display: flex; flex-wrap: wrap; justify-content: center; }
        .nav-bar a { margin: 5px 10px; }
        th, td { font-size: 12px; padding: 8px; }
        .stats-grid { grid-template-columns: 1fr; }
    }
</style>
'''

# ============================================
# FUNCIÓN PARA RENDERIZAR HTML
# ============================================
def render_page(title, content, current_user=None):
    user_section = ''
    if current_user and current_user.is_authenticated:
        user_section = f'<span style="color:#667eea;">Hola, {current_user.nombre}</span>'
    
    return f'''
    <!DOCTYPE html>
    <html>
    <head>
        <title>{title} - Patronato de Catacocha</title>
        {CSS}
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    </head>
    <body>
        <div class="nav-bar">
            <span class="brand"><i class="fas fa-hospital"></i> Patronato de Catacocha</span>
            <div>
                <a href="/"><i class="fas fa-home"></i> Inicio</a>
                {f'<a href="/agendar"><i class="fas fa-calendar-plus"></i> Agendar</a>' if current_user and current_user.is_authenticated else ''}
                {f'<a href="/mis-turnos"><i class="fas fa-calendar-check"></i> Mis Turnos</a>' if current_user and current_user.is_authenticated else ''}
                {f'<a href="/perfil"><i class="fas fa-user"></i> Mi Perfil</a>' if current_user and current_user.is_authenticated else ''}
                {f'<a href="/logout"><i class="fas fa-sign-out-alt"></i> Salir</a>' if current_user and current_user.is_authenticated else ''}
                {f'<a href="/login"><i class="fas fa-sign-in-alt"></i> Login</a>' if not (current_user and current_user.is_authenticated) else ''}
                {f'<a href="/registro"><i class="fas fa-user-plus"></i> Registro</a>' if not (current_user and current_user.is_authenticated) else ''}
            </div>
        </div>
        {content}
        <div class="footer">
            <p>&copy; 2024 Patronato de Catacocha - Sistema de Gestión de Turnos</p>
        </div>
    </body>
    </html>
    '''

# ============================================
# RUTAS PRINCIPALES
# ============================================

@app.route('/')
def index():
    # Obtener estadísticas
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM turnos WHERE estado = 'Programado'")
        turnos_programados = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM usuarios")
        total_usuarios = cursor.fetchone()[0]
        cursor.close()
        conn.close()
    except:
        turnos_programados = 0
        total_usuarios = 0
    
    content = f'''
    <div class="container container-large">
        <h2><i class="fas fa-church"></i> Sistema de Agendamiento de Turnos</h2>
        
        <div class="stats-grid">
            <div class="stat-card"><h3>{total_usuarios}</h3><p>Usuarios Registrados</p></div>
            <div class="stat-card"><h3>{turnos_programados}</h3><p>Turnos Programados</p></div>
            <div class="stat-card"><h3>8</h3><p>Especialidades</p></div>
        </div>
        
        <div class="card-grid">
            <a href="/agendar" class="service-card">
                <i class="fas fa-calendar-plus" style="font-size: 2rem;"></i>
                <h3>Agendar Turno</h3>
                <p>Solicita una cita médica en línea</p>
            </a>
            <a href="/mis-turnos" class="service-card">
                <i class="fas fa-calendar-check" style="font-size: 2rem;"></i>
                <h3>Mis Turnos</h3>
                <p>Consulta y gestiona tus citas</p>
            </a>
            <a href="/perfil" class="service-card">
                <i class="fas fa-user-circle" style="font-size: 2rem;"></i>
                <h3>Mi Perfil</h3>
                <p>Actualiza tu información personal</p>
            </a>
        </div>
    </div>
    '''
    return render_page('Inicio', content, current_user)

# ============================================
# AUTENTICACIÓN
# ============================================

@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm = request.form.get('confirm_password')
        
        if password != confirm:
            content = f'<div class="container"><div class="message error">❌ Las contraseñas no coinciden</div><div class="link"><a href="/registro">Volver</a></div></div>'
            return render_page('Error', content)
        
        password_hash = generate_password_hash(password)
        try:
            conn = get_db()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO usuarios (nombre, email, password) VALUES (%s, %s, %s)", (nombre, email, password_hash))
            conn.commit()
            cursor.close()
            conn.close()
            content = f'<div class="container"><div class="message success">✅ ¡Registro exitoso! Ahora puedes iniciar sesión.</div><div class="link"><a href="/login">Iniciar Sesión</a></div></div>'
            return render_page('Registro Exitoso', content)
        except Exception as e:
            content = f'<div class="container"><div class="message error">❌ Error: {e}</div><div class="link"><a href="/registro">Volver</a></div></div>'
            return render_page('Error', content)
    
    content = '''
    <div class="container">
        <h2><i class="fas fa-user-plus"></i> Registro de Usuario</h2>
        <form method="POST">
            <div class="form-group"><label><i class="fas fa-user"></i> Nombre completo</label><input type="text" name="nombre" required placeholder="Ingresa tu nombre"></div>
            <div class="form-group"><label><i class="fas fa-envelope"></i> Email</label><input type="email" name="email" required placeholder="correo@ejemplo.com"></div>
            <div class="form-group"><label><i class="fas fa-lock"></i> Contraseña</label><input type="password" name="password" required placeholder="Mínimo 6 caracteres"></div>
            <div class="form-group"><label><i class="fas fa-lock"></i> Confirmar contraseña</label><input type="password" name="confirm_password" required placeholder="Repite tu contraseña"></div>
            <button type="submit"><i class="fas fa-check"></i> Registrarse</button>
        </form>
        <div class="link">¿Ya tienes cuenta? <a href="/login">Inicia sesión aquí</a></div>
    </div>
    '''
    return render_page('Registro', content)

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
            content = '<div class="container"><div class="message error">❌ Credenciales incorrectas</div><div class="link"><a href="/login">Volver</a></div></div>'
            return render_page('Error', content)
        except Exception as e:
            content = f'<div class="container"><div class="message error">❌ Error: {e}</div><div class="link"><a href="/login">Volver</a></div></div>'
            return render_page('Error', content)
    
    content = '''
    <div class="container">
        <h2><i class="fas fa-sign-in-alt"></i> Iniciar Sesión</h2>
        <form method="POST">
            <div class="form-group"><label><i class="fas fa-envelope"></i> Email</label><input type="email" name="email" required placeholder="correo@ejemplo.com"></div>
            <div class="form-group"><label><i class="fas fa-lock"></i> Contraseña</label><input type="password" name="password" required placeholder="Ingresa tu contraseña"></div>
            <button type="submit"><i class="fas fa-arrow-right"></i> Ingresar</button>
        </form>
        <div class="link">¿No tienes cuenta? <a href="/registro">Regístrate aquí</a></div>
    </div>
    '''
    return render_page('Login', content)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    content = '<div class="container"><div class="message success">✅ Sesión cerrada correctamente</div><div class="link"><a href="/">Volver al inicio</a></div></div>'
    return render_page('Sesión Cerrada', content)

@app.route('/perfil')
@login_required
def perfil():
    content = f'''
    <div class="container">
        <h2><i class="fas fa-user-circle"></i> Mi Perfil</h2>
        <div class="form-group"><label><i class="fas fa-user"></i> Nombre</label><input type="text" value="{current_user.nombre}" disabled></div>
        <div class="form-group"><label><i class="fas fa-envelope"></i> Email</label><input type="email" value="{current_user.email}" disabled></div>
        <div class="form-group"><label><i class="fas fa-calendar"></i> Miembro desde</label><input type="text" value="2024" disabled></div>
        <div class="link"><a href="/agendar"><i class="fas fa-calendar-plus"></i> Agendar turno</a> | <a href="/mis-turnos"><i class="fas fa-calendar-check"></i> Ver mis turnos</a></div>
    </div>
    '''
    return render_page('Mi Perfil', content, current_user)

# ============================================
# AGENDAR TURNO
# ============================================

@app.route('/agendar', methods=['GET', 'POST'])
@login_required
def agendar_turno():
    try:
        conn = get_db()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM servicios ORDER BY nombre")
        servicios = cursor.fetchall()
        cursor.close()
        conn.close()
    except:
        servicios = []
    
    if request.method == 'POST':
        try:
            servicio_id = request.form.get('servicio_id')
            conn = get_db()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT nombre FROM servicios WHERE id = %s", (servicio_id,))
            servicio = cursor.fetchone()
            servicio_nombre = servicio['nombre'] if servicio else 'Medicina General'
            
            datos = (
                current_user.id,
                request.form.get('nombre_completo'),
                request.form.get('cedula'),
                request.form.get('telefono'),
                servicio_id,
                servicio_nombre,
                request.form.get('fecha'),
                request.form.get('hora'),
                request.form.get('motivo')
            )
            
            cursor.execute('''
                INSERT INTO turnos (usuario_id, nombre_completo, cedula, telefono, servicio_id, servicio_nombre, fecha, hora, motivo)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            ''', datos)
            conn.commit()
            cursor.close()
            conn.close()
            
            content = f'''
            <div class="container">
                <div class="message success">✅ ¡Turno agendado exitosamente!</div>
                <div class="link"><a href="/mis-turnos"><i class="fas fa-calendar-check"></i> Ver mis turnos</a> | <a href="/"><i class="fas fa-home"></i> Inicio</a></div>
            </div>
            '''
            return render_page('Turno Agendado', content, current_user)
        except Exception as e:
            content = f'<div class="container"><div class="message error">❌ Error: {e}</div><div class="link"><a href="/agendar">Volver</a></div></div>'
            return render_page('Error', content, current_user)
    
    servicios_html = ''
    for s in servicios:
        servicios_html += f'<option value="{s["id"]}">{s["nombre"]}</option>'
    
    content = f'''
    <div class="container">
        <h2><i class="fas fa-calendar-plus"></i> Agendar Nuevo Turno</h2>
        <form method="POST">
            <div class="form-group"><label><i class="fas fa-user"></i> Nombre completo</label><input type="text" name="nombre_completo" value="{current_user.nombre}" required></div>
            <div class="row">
                <div class="col"><div class="form-group"><label><i class="fas fa-id-card"></i> Cédula</label><input type="text" name="cedula" placeholder="Ingresa tu cédula" required></div></div>
                <div class="col"><div class="form-group"><label><i class="fas fa-phone"></i> Teléfono</label><input type="tel" name="telefono" placeholder="0991234567" required></div></div>
            </div>
            <div class="form-group"><label><i class="fas fa-stethoscope"></i> Servicio médico</label><select name="servicio_id" required><option value="">Selecciona un servicio</option>{servicios_html}</select></div>
            <div class="row">
                <div class="col"><div class="form-group"><label><i class="fas fa-calendar"></i> Fecha</label><input type="date" name="fecha" required></div></div>
                <div class="col"><div class="form-group"><label><i class="fas fa-clock"></i> Hora</label><input type="time" name="hora" required></div></div>
            </div>
            <div class="form-group"><label><i class="fas fa-comment"></i> Motivo de consulta</label><textarea name="motivo" rows="3" placeholder="Describe el motivo de tu consulta"></textarea></div>
            <button type="submit"><i class="fas fa-save"></i> Agendar Turno</button>
            <a href="/"><button type="button" class="btn-secondary"><i class="fas fa-times"></i> Cancelar</button></a>
        </form>
    </div>
    '''
    return render_page('Agendar Turno', content, current_user)

# ============================================
# MIS TURNOS
# ============================================

@app.route('/mis-turnos')
@login_required
def mis_turnos():
    try:
        conn = get_db()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM turnos WHERE usuario_id = %s ORDER BY fecha DESC, hora DESC", (current_user.id,))
        turnos = cursor.fetchall()
        cursor.close()
        conn.close()
        
        if not turnos:
            turnos_html = '<p style="text-align: center; padding: 40px;">No tienes turnos agendados. <a href="/agendar">Agendar turno</a></p>'
        else:
            turnos_html = '''
            <table>
                <thead><tr><th>Fecha</th><th>Hora</th><th>Servicio</th><th>Estado</th><th>Acciones</th></tr></thead>
                <tbody>
            '''
            for t in turnos:
                estado_class = {'Programado': 'badge-programado', 'Confirmado': 'badge-confirmado', 'Cancelado': 'badge-cancelado'}.get(t['estado'], 'badge-programado')
                turnos_html += f'''
                    <tr>
                        <td>{t['fecha']}</td><td>{t['hora']}</td><td>{t['servicio_nombre']}</td>
                        <td><span class="badge {estado_class}">{t['estado']}</span></td>
                        <td><a href="/cancelar-turno/{t['id']}" onclick="return confirm('¿Cancelar este turno?')"><button class="btn-sm btn-delete"><i class="fas fa-trash"></i> Cancelar</button></a></td>
                    </tr>
                '''
            turnos_html += '</tbody></table>'
        
        content = f'''
        <div class="container container-large">
            <h2><i class="fas fa-calendar-check"></i> Mis Turnos</h2>
            {turnos_html}
            <div class="link"><a href="/agendar"><i class="fas fa-plus-circle"></i> Agendar nuevo turno</a></div>
        </div>
        '''
        return render_page('Mis Turnos', content, current_user)
    except Exception as e:
        content = f'<div class="container"><div class="message error">❌ Error: {e}</div><div class="link"><a href="/">Volver</a></div></div>'
        return render_page('Error', content, current_user)

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
    except:
        return redirect(url_for('mis_turnos'))

# ============================================
# INICIO DE LA APLICACIÓN
# ============================================

if __name__ == '__main__':
    print('''
    ╔══════════════════════════════════════════════════════════╗
    ║     🏛️ PATRONATO DE CATACOCHA - SISTEMA DE TURNOS        ║
    ║                                                          ║
    ║     ✅ Base de datos: MySQL (turnos_db)                  ║
    ║     ✅ Servidor: http://127.0.0.1:5000                   ║
    ║     ✅ Estado: Listo para usar                           ║
    ╚══════════════════════════════════════════════════════════╝
    ''')
    app.run(debug=True)
