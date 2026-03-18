# app.py
# Aplicación Flask Principal - Patronato de Catacocha
# Semana 14: Sistema de Autenticación con Flask-Login

from flask import Flask, render_template, request, redirect, url_for, flash
from datetime import datetime
import os

# Flask-Login
from flask_login import LoginManager, login_user, logout_user, login_required, current_user

# Importar formularios
from form import ProductoForm, TurnoForm
from forms import RegistroForm, LoginForm, CambioPasswordForm

# Importar modelos
from models import Usuario

# Importar persistencia
from inventario.inventario import PersistenciaTXT, PersistenciaJSON, PersistenciaCSV
from inventario.productos import Producto

# Importar SQLAlchemy
from inventario.bd import db, ProductoModel

# Importar conexión MySQL
from Conexion.conexion import get_db, close_db
from mysql.connector import Error

# Importar decoradores
from decorators import login_required_message, admin_required

app = Flask(__name__)

# Configuración
app.config['SECRET_KEY'] = 'clave-secreta-patronato-catacocha-2024-segura'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///turnos.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# ============================================
# CONFIGURACIÓN DE FLASK-LOGIN
# ============================================
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Por favor, inicie sesión para acceder a esta página'
login_manager.login_message_category = 'info'

@login_manager.user_loader
def load_user(user_id):
    """Carga un usuario desde la base de datos"""
    return Usuario.get_by_id(int(user_id))

# Inicializar SQLAlchemy
db.init_app(app)

# Crear tablas SQLAlchemy
with app.app_context():
    db.create_all()
    print("✅ Tablas de SQLAlchemy creadas/verificadas")

# Registrar la función para cerrar conexión MySQL
app.teardown_appcontext(close_db)

# Instancias de persistencia
txt_persistencia = PersistenciaTXT()
json_persistencia = PersistenciaJSON()
csv_persistencia = PersistenciaCSV()

# ============================================
# RUTAS PÚBLICAS (accesibles sin autenticación)
# ============================================

@app.route('/')
def index():
    '''Página principal'''
    return render_template('index.html')

@app.route('/about')
def about():
    '''Página Acerca de'''
    return render_template('about.html')

@app.route('/servicios')
def servicios():
    '''Página de servicios'''
    return render_template('servicios.html')

@app.route('/contacto')
def contacto():
    '''Página de contacto'''
    return render_template('contacto.html')

# ============================================
# RUTAS DE AUTENTICACIÓN
# ============================================

@app.route('/registro', methods=['GET', 'POST'])
def registro():
    '''Registro de nuevos usuarios'''
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = RegistroForm()
    
    if form.validate_on_submit():
        usuario = Usuario.create(
            nombre=form.nombre.data,
            email=form.email.data,
            password=form.password.data
        )
        
        if usuario:
            flash('✅ Registro exitoso. Ahora puedes iniciar sesión.', 'success')
            return redirect(url_for('login'))
        else:
            flash('❌ Error al registrar usuario. Intente nuevamente.', 'danger')
    
    return render_template('registro.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    '''Inicio de sesión'''
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = LoginForm()
    
    if form.validate_on_submit():
        usuario = Usuario.get_by_email(form.email.data)
        
        if usuario and usuario.check_password(form.password.data):
            login_user(usuario)
            flash(f'✅ Bienvenido, {usuario.nombre}!', 'success')
            
            # Redirigir a la página solicitada o al inicio
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('index'))
        else:
            flash('❌ Email o contraseña incorrectos', 'danger')
    
    return render_template('login.html', form=form)

@app.route('/logout')
def logout():
    '''Cierre de sesión'''
    logout_user()
    flash('✅ Sesión cerrada correctamente', 'success')
    return redirect(url_for('index'))

@app.route('/perfil')
@login_required_message('Debes iniciar sesión para ver tu perfil')
def perfil():
    '''Perfil de usuario'''
    return render_template('perfil.html')

@app.route('/cambiar-password', methods=['GET', 'POST'])
@login_required_message('Debes iniciar sesión para cambiar tu contraseña')
def cambiar_password():
    '''Cambiar contraseña'''
    form = CambioPasswordForm()
    
    if form.validate_on_submit():
        if current_user.check_password(form.password_actual.data):
            if Usuario.update_password(current_user.id, form.nueva_password.data):
                flash('✅ Contraseña actualizada correctamente', 'success')
                return redirect(url_for('perfil'))
            else:
                flash('❌ Error al actualizar la contraseña', 'danger')
        else:
            flash('❌ La contraseña actual es incorrecta', 'danger')
    
    return render_template('cambiar_password.html', form=form)

# ============================================
# RUTAS PROTEGIDAS (requieren autenticación)
# ============================================

@app.route('/cita/<paciente>')
@login_required
def cita(paciente):
    '''Ruta dinámica para citas (protegida)'''
    fecha_actual = datetime.now().strftime("%d/%m/%Y")
    return render_template('cita.html', paciente=paciente, fecha=fecha_actual)

@app.route('/citas')
@login_required_message('Inicia sesión para ver tus citas')
def citas():
    '''Listado de citas (protegido)'''
    citas_ejemplo = [
        {'paciente': 'María González', 'fecha': '15/03/2024', 'servicio': 'Medicina General'},
        {'paciente': 'Juan Pérez', 'fecha': '16/03/2024', 'servicio': 'Odontología'},
        {'paciente': 'Ana Rodríguez', 'fecha': '17/03/2024', 'servicio': 'Trabajo Social'}
    ]
    return render_template('citas.html', citas=citas_ejemplo)

# ============================================
# RUTAS DE PERSISTENCIA (protegidas)
# ============================================

@app.route('/productos')
@login_required
def productos():
    '''Lista todos los productos (protegido)'''
    productos = ProductoModel.query.all()
    return render_template('productos.html', productos=productos)

@app.route('/productos/nuevo', methods=['GET', 'POST'])
@login_required
def producto_nuevo():
    '''Crea un nuevo producto (protegido)'''
    form = ProductoForm()
    
    if form.validate_on_submit():
        producto = ProductoModel(
            nombre=form.nombre.data,
            descripcion=form.descripcion.data,
            precio=form.precio.data,
            cantidad=form.cantidad.data
        )
        db.session.add(producto)
        db.session.commit()
        
        datos_producto = {
            'nombre': form.nombre.data,
            'descripcion': form.descripcion.data,
            'precio': form.precio.data,
            'cantidad': form.cantidad.data
        }
        
        txt_persistencia.guardar(f"Producto: {datos_producto}")
        json_persistencia.guardar(datos_producto)
        csv_persistencia.guardar(datos_producto)
        
        flash('✅ Producto creado exitosamente', 'success')
        return redirect(url_for('productos'))
    
    return render_template('producto_form.html', form=form, titulo='Nuevo Producto')

@app.route('/productos/editar/<int:id>', methods=['GET', 'POST'])
@login_required
def producto_editar(id):
    '''Edita un producto existente (protegido)'''
    producto = ProductoModel.query.get_or_404(id)
    form = ProductoForm(obj=producto)
    
    if form.validate_on_submit():
        producto.nombre = form.nombre.data
        producto.descripcion = form.descripcion.data
        producto.precio = form.precio.data
        producto.cantidad = form.cantidad.data
        db.session.commit()
        flash('✅ Producto actualizado exitosamente', 'success')
        return redirect(url_for('productos'))
    
    return render_template('producto_form.html', form=form, titulo='Editar Producto')

@app.route('/productos/eliminar/<int:id>')
@login_required
def producto_eliminar(id):
    '''Elimina un producto (protegido)'''
    producto = ProductoModel.query.get_or_404(id)
    db.session.delete(producto)
    db.session.commit()
    flash('✅ Producto eliminado exitosamente', 'success')
    return redirect(url_for('productos'))

@app.route('/datos')
@login_required_message('Inicia sesión para ver los datos almacenados')
def ver_datos():
    '''Muestra todos los datos almacenados (protegido)'''
    datos_txt = txt_persistencia.leer()
    datos_json = json_persistencia.leer()
    datos_csv = csv_persistencia.leer()
    productos_sql = ProductoModel.query.all()
    
    return render_template('datos.html', 
                          datos_txt=datos_txt,
                          datos_json=datos_json,
                          datos_csv=datos_csv,
                          productos_sql=productos_sql)

# ============================================
# RUTAS MYSQL (protegidas)
# ============================================

@app.route('/mysql/test')
@login_required
def mysql_test():
    '''Prueba la conexión a MySQL (protegido)'''
    try:
        db_mysql = get_db()
        if db_mysql.connection and db_mysql.connection.is_connected():
            return """
            <!DOCTYPE html>
            <html>
            <head>
                <title>MySQL Test</title>
                <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
            </head>
            <body>
                <div class="container mt-5 text-center">
                    <div class="alert alert-success">
                        <h1>✅ CONEXIÓN MYSQL EXITOSA</h1>
                        <p>La aplicación está conectada a MySQL correctamente.</p>
                    </div>
                    <div class="mt-4">
                        <a href='/mysql/usuarios' class="btn btn-primary">Ver Usuarios</a>
                        <a href='/mysql/pacientes' class="btn btn-primary">Ver Pacientes</a>
                        <a href='/mysql/medicos' class="btn btn-primary">Ver Médicos</a>
                        <a href='/mysql/turnos' class="btn btn-primary">Ver Turnos</a>
                        <a href='/' class="btn btn-secondary">Volver al Inicio</a>
                    </div>
                </div>
            </body>
            </html>
            """
        else:
            return "❌ No conectado"
    except Exception as e:
        return f"❌ Error: {str(e)}"

# ---------- CRUD PARA USUARIOS (solo usuarios autenticados) ----------

@app.route('/mysql/usuarios')
@login_required
def mysql_listar_usuarios():
    """Listar todos los usuarios (protegido)"""
    db_mysql = get_db()
    usuarios = db_mysql.fetch_all("SELECT * FROM usuarios ORDER BY id_usuario DESC")
    return render_template('mysql_usuarios.html', usuarios=usuarios)

@app.route('/mysql/usuarios/nuevo', methods=['GET', 'POST'])
@login_required
def mysql_nuevo_usuario():
    """Insertar nuevo usuario (protegido)"""
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        mail = request.form.get('mail')
        password = request.form.get('password')
        
        db_mysql = get_db()
        query = "INSERT INTO usuarios (nombre, mail, password) VALUES (%s, %s, %s)"
        result = db_mysql.execute_query(query, (nombre, mail, password))
        
        if result > 0:
            flash('✅ Usuario insertado correctamente', 'success')
        else:
            flash('❌ Error al insertar usuario', 'danger')
        
        return redirect(url_for('mysql_listar_usuarios'))
    
    return render_template('mysql_usuario_form.html', accion='Nuevo Usuario')

@app.route('/mysql/usuarios/editar/<int:id>', methods=['GET', 'POST'])
@login_required
def mysql_editar_usuario(id):
    """Modificar usuario (protegido)"""
    db_mysql = get_db()
    
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        mail = request.form.get('mail')
        password = request.form.get('password')
        
        query = "UPDATE usuarios SET nombre=%s, mail=%s, password=%s WHERE id_usuario=%s"
        result = db_mysql.execute_query(query, (nombre, mail, password, id))
        
        if result > 0:
            flash('✅ Usuario actualizado correctamente', 'success')
        else:
            flash('❌ Error al actualizar usuario', 'danger')
        
        return redirect(url_for('mysql_listar_usuarios'))
    
    usuario = db_mysql.fetch_one("SELECT * FROM usuarios WHERE id_usuario = %s", (id,))
    if not usuario:
        flash('❌ Usuario no encontrado', 'danger')
        return redirect(url_for('mysql_listar_usuarios'))
    
    return render_template('mysql_usuario_form.html', usuario=usuario, accion='Editar Usuario')

@app.route('/mysql/usuarios/eliminar/<int:id>')
@login_required
def mysql_eliminar_usuario(id):
    """Eliminar usuario (protegido)"""
    db_mysql = get_db()
    result = db_mysql.execute_query("DELETE FROM usuarios WHERE id_usuario = %s", (id,))
    
    if result > 0:
        flash('✅ Usuario eliminado correctamente', 'success')
    else:
        flash('❌ Error al eliminar usuario', 'danger')
    
    return redirect(url_for('mysql_listar_usuarios'))

# ---------- CRUD PARA PACIENTES (protegido) ----------

@app.route('/mysql/pacientes')
@login_required
def mysql_listar_pacientes():
    """Listar todos los pacientes (protegido)"""
    db_mysql = get_db()
    pacientes = db_mysql.fetch_all("SELECT * FROM pacientes ORDER BY id DESC")
    return render_template('mysql_pacientes.html', pacientes=pacientes)

@app.route('/mysql/pacientes/nuevo', methods=['GET', 'POST'])
@login_required
def mysql_nuevo_paciente():
    """Insertar nuevo paciente (protegido)"""
    if request.method == 'POST':
        datos = (
            request.form.get('cedula'),
            request.form.get('nombre'),
            request.form.get('apellido'),
            request.form.get('fecha_nacimiento') or None,
            request.form.get('telefono'),
            request.form.get('direccion'),
            request.form.get('email')
        )
        
        db_mysql = get_db()
        query = """INSERT INTO pacientes 
                  (cedula, nombre, apellido, fecha_nacimiento, telefono, direccion, email) 
                  VALUES (%s, %s, %s, %s, %s, %s, %s)"""
        result = db_mysql.execute_query(query, datos)
        
        if result > 0:
            flash('✅ Paciente insertado correctamente', 'success')
        else:
            flash('❌ Error al insertar paciente', 'danger')
        
        return redirect(url_for('mysql_listar_pacientes'))
    
    return render_template('mysql_paciente_form.html', accion='Nuevo Paciente')

@app.route('/mysql/pacientes/editar/<int:id>', methods=['GET', 'POST'])
@login_required
def mysql_editar_paciente(id):
    """Modificar paciente (protegido)"""
    db_mysql = get_db()
    
    if request.method == 'POST':
        datos = (
            request.form.get('cedula'),
            request.form.get('nombre'),
            request.form.get('apellido'),
            request.form.get('fecha_nacimiento') or None,
            request.form.get('telefono'),
            request.form.get('direccion'),
            request.form.get('email'),
            id
        )
        
        query = """UPDATE pacientes 
                  SET cedula=%s, nombre=%s, apellido=%s, fecha_nacimiento=%s, 
                      telefono=%s, direccion=%s, email=%s 
                  WHERE id=%s"""
        result = db_mysql.execute_query(query, datos)
        
        if result > 0:
            flash('✅ Paciente actualizado correctamente', 'success')
        else:
            flash('❌ Error al actualizar paciente', 'danger')
        
        return redirect(url_for('mysql_listar_pacientes'))
    
    paciente = db_mysql.fetch_one("SELECT * FROM pacientes WHERE id = %s", (id,))
    if not paciente:
        flash('❌ Paciente no encontrado', 'danger')
        return redirect(url_for('mysql_listar_pacientes'))
    
    return render_template('mysql_paciente_form.html', paciente=paciente, accion='Editar Paciente')

@app.route('/mysql/pacientes/eliminar/<int:id>')
@login_required
def mysql_eliminar_paciente(id):
    """Eliminar paciente (protegido)"""
    db_mysql = get_db()
    result = db_mysql.execute_query("DELETE FROM pacientes WHERE id = %s", (id,))
    
    if result > 0:
        flash('✅ Paciente eliminado correctamente', 'success')
    else:
        flash('❌ Error al eliminar paciente', 'danger')
    
    return redirect(url_for('mysql_listar_pacientes'))

# ---------- CRUD PARA MÉDICOS (protegido) ----------

@app.route('/mysql/medicos')
@login_required
def mysql_listar_medicos():
    """Listar todos los médicos (protegido)"""
    db_mysql = get_db()
    medicos = db_mysql.fetch_all("SELECT * FROM medicos ORDER BY id DESC")
    return render_template('mysql_medicos.html', medicos=medicos)

@app.route('/mysql/medicos/nuevo', methods=['GET', 'POST'])
@login_required
def mysql_nuevo_medico():
    """Insertar nuevo médico (protegido)"""
    if request.method == 'POST':
        datos = (
            request.form.get('cedula'),
            request.form.get('nombre'),
            request.form.get('apellido'),
            request.form.get('especialidad'),
            request.form.get('telefono'),
            request.form.get('email')
        )
        
        db_mysql = get_db()
        query = """INSERT INTO medicos 
                  (cedula, nombre, apellido, especialidad, telefono, email) 
                  VALUES (%s, %s, %s, %s, %s, %s)"""
        result = db_mysql.execute_query(query, datos)
        
        if result > 0:
            flash('✅ Médico insertado correctamente', 'success')
        else:
            flash('❌ Error al insertar médico', 'danger')
        
        return redirect(url_for('mysql_listar_medicos'))
    
    return render_template('mysql_medico_form.html', accion='Nuevo Médico')

@app.route('/mysql/medicos/editar/<int:id>', methods=['GET', 'POST'])
@login_required
def mysql_editar_medico(id):
    """Modificar médico (protegido)"""
    db_mysql = get_db()
    
    if request.method == 'POST':
        datos = (
            request.form.get('cedula'),
            request.form.get('nombre'),
            request.form.get('apellido'),
            request.form.get('especialidad'),
            request.form.get('telefono'),
            request.form.get('email'),
            id
        )
        
        query = """UPDATE medicos 
                  SET cedula=%s, nombre=%s, apellido=%s, especialidad=%s, 
                      telefono=%s, email=%s 
                  WHERE id=%s"""
        result = db_mysql.execute_query(query, datos)
        
        if result > 0:
            flash('✅ Médico actualizado correctamente', 'success')
        else:
            flash('❌ Error al actualizar médico', 'danger')
        
        return redirect(url_for('mysql_listar_medicos'))
    
    medico = db_mysql.fetch_one("SELECT * FROM medicos WHERE id = %s", (id,))
    if not medico:
        flash('❌ Médico no encontrado', 'danger')
        return redirect(url_for('mysql_listar_medicos'))
    
    return render_template('mysql_medico_form.html', medico=medico, accion='Editar Médico')

@app.route('/mysql/medicos/eliminar/<int:id>')
@login_required
def mysql_eliminar_medico(id):
    """Eliminar médico (protegido)"""
    db_mysql = get_db()
    result = db_mysql.execute_query("DELETE FROM medicos WHERE id = %s", (id,))
    
    if result > 0:
        flash('✅ Médico eliminado correctamente', 'success')
    else:
            flash('❌ Error al eliminar médico', 'danger')
    
    return redirect(url_for('mysql_listar_medicos'))

# ---------- CRUD PARA TURNOS (protegido) ----------

@app.route('/mysql/turnos')
@login_required
def mysql_listar_turnos():
    """Listar todos los turnos con información relacionada (protegido)"""
    db_mysql = get_db()
    query = """
        SELECT t.*, 
               p.nombre as paciente_nombre, p.apellido as paciente_apellido,
               m.nombre as medico_nombre, m.apellido as medico_apellido, m.especialidad
        FROM turnos t
        JOIN pacientes p ON t.paciente_id = p.id
        JOIN medicos m ON t.medico_id = m.id
        ORDER BY t.fecha DESC, t.hora DESC
    """
    turnos = db_mysql.fetch_all(query)
    return render_template('mysql_turnos.html', turnos=turnos)

@app.route('/mysql/turnos/nuevo', methods=['GET', 'POST'])
@login_required
def mysql_nuevo_turno():
    """Insertar nuevo turno (protegido)"""
    db_mysql = get_db()
    
    if request.method == 'POST':
        datos = (
            request.form.get('paciente_id'),
            request.form.get('medico_id'),
            request.form.get('fecha'),
            request.form.get('hora'),
            request.form.get('motivo'),
            request.form.get('estado', 'Programado')
        )
        
        query = """INSERT INTO turnos 
                  (paciente_id, medico_id, fecha, hora, motivo, estado) 
                  VALUES (%s, %s, %s, %s, %s, %s)"""
        result = db_mysql.execute_query(query, datos)
        
        if result > 0:
            flash('✅ Turno insertado correctamente', 'success')
        else:
            flash('❌ Error al insertar turno', 'danger')
        
        return redirect(url_for('mysql_listar_turnos'))
    
    pacientes = db_mysql.fetch_all("SELECT id, cedula, nombre, apellido FROM pacientes ORDER BY apellido")
    medicos = db_mysql.fetch_all("SELECT id, nombre, apellido, especialidad FROM medicos ORDER BY apellido")
    
    return render_template('mysql_turno_form.html', 
                          pacientes=pacientes, 
                          medicos=medicos, 
                          accion='Nuevo Turno')

@app.route('/mysql/turnos/editar/<int:id>', methods=['GET', 'POST'])
@login_required
def mysql_editar_turno(id):
    """Modificar turno (protegido)"""
    db_mysql = get_db()
    
    if request.method == 'POST':
        datos = (
            request.form.get('paciente_id'),
            request.form.get('medico_id'),
            request.form.get('fecha'),
            request.form.get('hora'),
            request.form.get('motivo'),
            request.form.get('estado'),
            id
        )
        
        query = """UPDATE turnos 
                  SET paciente_id=%s, medico_id=%s, fecha=%s, hora=%s, motivo=%s, estado=%s 
                  WHERE id=%s"""
        result = db_mysql.execute_query(query, datos)
        
        if result > 0:
            flash('✅ Turno actualizado correctamente', 'success')
        else:
            flash('❌ Error al actualizar turno', 'danger')
        
        return redirect(url_for('mysql_listar_turnos'))
    
    turno = db_mysql.fetch_one("SELECT * FROM turnos WHERE id = %s", (id,))
    if not turno:
        flash('❌ Turno no encontrado', 'danger')
        return redirect(url_for('mysql_listar_turnos'))
    
    pacientes = db_mysql.fetch_all("SELECT id, cedula, nombre, apellido FROM pacientes ORDER BY apellido")
    medicos = db_mysql.fetch_all("SELECT id, nombre, apellido, especialidad FROM medicos ORDER BY apellido")
    
    return render_template('mysql_turno_form.html', 
                          turno=turno,
                          pacientes=pacientes, 
                          medicos=medicos, 
                          accion='Editar Turno')

@app.route('/mysql/turnos/eliminar/<int:id>')
@login_required
def mysql_eliminar_turno(id):
    """Eliminar turno (protegido)"""
    db_mysql = get_db()
    result = db_mysql.execute_query("DELETE FROM turnos WHERE id = %s", (id,))
    
    if result > 0:
        flash('✅ Turno eliminado correctamente', 'success')
    else:
        flash('❌ Error al eliminar turno', 'danger')
    
    return redirect(url_for('mysql_listar_turnos'))

# ============================================
# INICIO DE LA APLICACIÓN
# ============================================

if __name__ == '__main__':
    app.run(debug=True)