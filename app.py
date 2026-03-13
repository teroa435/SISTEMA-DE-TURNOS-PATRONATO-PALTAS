# app.py
# Aplicación Flask Principal - Patronato de Catacocha
# Semana 12: Persistencia con Archivos y SQLAlchemy

from flask import Flask, render_template, request, redirect, url_for, flash
from datetime import datetime
import os

# Importar formularios
from form import ProductoForm, TurnoForm

# Importar persistencia
from inventario.inventario import PersistenciaTXT, PersistenciaJSON, PersistenciaCSV
from inventario.productos import Producto

# Importar SQLAlchemy
from inventario.bd import db, ProductoModel

app = Flask(__name__)

# Configuración
app.config['SECRET_KEY'] = 'clave-secreta-patronato-catacocha-2024'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///turnos.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicializar SQLAlchemy
db.init_app(app)

# Crear tablas
with app.app_context():
    db.create_all()
    print("✅ Tablas de SQLAlchemy creadas/verificadas")

# Instancias de persistencia
txt_persistencia = PersistenciaTXT()
json_persistencia = PersistenciaJSON()
csv_persistencia = PersistenciaCSV()

# ============================================
# RUTAS DE LA APLICACIÓN WEB (semanas anteriores)
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

@app.route('/cita/<paciente>')
def cita(paciente):
    '''Ruta dinámica para citas'''
    fecha_actual = datetime.now().strftime("%d/%m/%Y")
    return render_template('cita.html', paciente=paciente, fecha=fecha_actual)

@app.route('/citas')
def citas():
    '''Listado de citas'''
    citas_ejemplo = [
        {'paciente': 'María González', 'fecha': '15/03/2024', 'servicio': 'Medicina General'},
        {'paciente': 'Juan Pérez', 'fecha': '16/03/2024', 'servicio': 'Odontología'},
        {'paciente': 'Ana Rodríguez', 'fecha': '17/03/2024', 'servicio': 'Trabajo Social'}
    ]
    return render_template('citas.html', citas=citas_ejemplo)

# ============================================
# RUTAS DE PERSISTENCIA (Semana 12)
# ============================================

@app.route('/productos')
def productos():
    '''Lista todos los productos usando SQLAlchemy'''
    productos = ProductoModel.query.all()
    return render_template('productos.html', productos=productos)

@app.route('/productos/nuevo', methods=['GET', 'POST'])
def producto_nuevo():
    '''Crea un nuevo producto'''
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
        
        flash('Producto creado exitosamente', 'success')
        return redirect(url_for('productos'))
    
    return render_template('producto_form.html', form=form, titulo='Nuevo Producto')

@app.route('/datos')
def ver_datos():
    '''Muestra todos los datos almacenados en diferentes formatos'''
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
# CRUD COMPLETO PARA MYSQL (Semana 13)
# ============================================
from Conexion.conexion import get_db, close_db

# Registrar la función para cerrar conexión
app.teardown_appcontext(close_db)

# ---------- CRUD PARA USUARIOS ----------

@app.route('/mysql/usuarios')
def mysql_listar_usuarios():
    """Listar todos los usuarios"""
    db = get_db()
    usuarios = db.fetch_all("SELECT * FROM usuarios ORDER BY id_usuario DESC")
    return render_template('mysql_usuarios.html', usuarios=usuarios)

@app.route('/mysql/usuarios/nuevo', methods=['GET', 'POST'])
def mysql_nuevo_usuario():
    """Insertar nuevo usuario"""
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        mail = request.form.get('mail')
        password = request.form.get('password')
        
        db = get_db()
        query = "INSERT INTO usuarios (nombre, mail, password) VALUES (%s, %s, %s)"
        result = db.execute_query(query, (nombre, mail, password))
        
        if result > 0:
            flash('✅ Usuario insertado correctamente', 'success')
        else:
            flash('❌ Error al insertar usuario', 'danger')
        
        return redirect(url_for('mysql_listar_usuarios'))
    
    return render_template('mysql_usuario_form.html', accion='Nuevo Usuario')

@app.route('/mysql/usuarios/editar/<int:id>', methods=['GET', 'POST'])
def mysql_editar_usuario(id):
    """Modificar usuario"""
    db = get_db()
    
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        mail = request.form.get('mail')
        password = request.form.get('password')
        
        query = "UPDATE usuarios SET nombre=%s, mail=%s, password=%s WHERE id_usuario=%s"
        result = db.execute_query(query, (nombre, mail, password, id))
        
        if result > 0:
            flash('✅ Usuario actualizado correctamente', 'success')
        else:
            flash('❌ Error al actualizar usuario', 'danger')
        
        return redirect(url_for('mysql_listar_usuarios'))
    
    usuario = db.fetch_one("SELECT * FROM usuarios WHERE id_usuario = %s", (id,))
    if not usuario:
        flash('❌ Usuario no encontrado', 'danger')
        return redirect(url_for('mysql_listar_usuarios'))
    
    return render_template('mysql_usuario_form.html', usuario=usuario, accion='Editar Usuario')

@app.route('/mysql/usuarios/eliminar/<int:id>')
def mysql_eliminar_usuario(id):
    """Eliminar usuario"""
    db = get_db()
    result = db.execute_query("DELETE FROM usuarios WHERE id_usuario = %s", (id,))
    
    if result > 0:
        flash('✅ Usuario eliminado correctamente', 'success')
    else:
        flash('❌ Error al eliminar usuario', 'danger')
    
    return redirect(url_for('mysql_listar_usuarios'))

# ---------- CRUD PARA PACIENTES ----------

@app.route('/mysql/pacientes')
def mysql_listar_pacientes():
    """Listar todos los pacientes"""
    db = get_db()
    pacientes = db.fetch_all("SELECT * FROM pacientes ORDER BY id DESC")
    return render_template('mysql_pacientes.html', pacientes=pacientes)

@app.route('/mysql/pacientes/nuevo', methods=['GET', 'POST'])
def mysql_nuevo_paciente():
    """Insertar nuevo paciente"""
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
        
        db = get_db()
        query = """INSERT INTO pacientes 
                  (cedula, nombre, apellido, fecha_nacimiento, telefono, direccion, email) 
                  VALUES (%s, %s, %s, %s, %s, %s, %s)"""
        result = db.execute_query(query, datos)
        
        if result > 0:
            flash('✅ Paciente insertado correctamente', 'success')
        else:
            flash('❌ Error al insertar paciente', 'danger')
        
        return redirect(url_for('mysql_listar_pacientes'))
    
    return render_template('mysql_paciente_form.html', accion='Nuevo Paciente')

@app.route('/mysql/pacientes/editar/<int:id>', methods=['GET', 'POST'])
def mysql_editar_paciente(id):
    """Modificar paciente"""
    db = get_db()
    
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
        result = db.execute_query(query, datos)
        
        if result > 0:
            flash('✅ Paciente actualizado correctamente', 'success')
        else:
            flash('❌ Error al actualizar paciente', 'danger')
        
        return redirect(url_for('mysql_listar_pacientes'))
    
    paciente = db.fetch_one("SELECT * FROM pacientes WHERE id = %s", (id,))
    if not paciente:
        flash('❌ Paciente no encontrado', 'danger')
        return redirect(url_for('mysql_listar_pacientes'))
    
    return render_template('mysql_paciente_form.html', paciente=paciente, accion='Editar Paciente')

@app.route('/mysql/pacientes/eliminar/<int:id>')
def mysql_eliminar_paciente(id):
    """Eliminar paciente"""
    db = get_db()
    result = db.execute_query("DELETE FROM pacientes WHERE id = %s", (id,))
    
    if result > 0:
        flash('✅ Paciente eliminado correctamente', 'success')
    else:
        flash('❌ Error al eliminar paciente', 'danger')
    
    return redirect(url_for('mysql_listar_pacientes'))

# ---------- CRUD PARA MÉDICOS ----------

@app.route('/mysql/medicos')
def mysql_listar_medicos():
    """Listar todos los médicos"""
    db = get_db()
    medicos = db.fetch_all("SELECT * FROM medicos ORDER BY id DESC")
    return render_template('mysql_medicos.html', medicos=medicos)

@app.route('/mysql/medicos/nuevo', methods=['GET', 'POST'])
def mysql_nuevo_medico():
    """Insertar nuevo médico"""
    if request.method == 'POST':
        datos = (
            request.form.get('cedula'),
            request.form.get('nombre'),
            request.form.get('apellido'),
            request.form.get('especialidad'),
            request.form.get('telefono'),
            request.form.get('email')
        )
        
        db = get_db()
        query = """INSERT INTO medicos 
                  (cedula, nombre, apellido, especialidad, telefono, email) 
                  VALUES (%s, %s, %s, %s, %s, %s)"""
        result = db.execute_query(query, datos)
        
        if result > 0:
            flash('✅ Médico insertado correctamente', 'success')
        else:
            flash('❌ Error al insertar médico', 'danger')
        
        return redirect(url_for('mysql_listar_medicos'))
    
    return render_template('mysql_medico_form.html', accion='Nuevo Médico')

@app.route('/mysql/medicos/editar/<int:id>', methods=['GET', 'POST'])
def mysql_editar_medico(id):
    """Modificar médico"""
    db = get_db()
    
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
        result = db.execute_query(query, datos)
        
        if result > 0:
            flash('✅ Médico actualizado correctamente', 'success')
        else:
            flash('❌ Error al actualizar médico', 'danger')
        
        return redirect(url_for('mysql_listar_medicos'))
    
    medico = db.fetch_one("SELECT * FROM medicos WHERE id = %s", (id,))
    if not medico:
        flash('❌ Médico no encontrado', 'danger')
        return redirect(url_for('mysql_listar_medicos'))
    
    return render_template('mysql_medico_form.html', medico=medico, accion='Editar Médico')

@app.route('/mysql/medicos/eliminar/<int:id>')
def mysql_eliminar_medico(id):
    """Eliminar médico"""
    db = get_db()
    result = db.execute_query("DELETE FROM medicos WHERE id = %s", (id,))
    
    if result > 0:
        flash('✅ Médico eliminado correctamente', 'success')
    else:
        flash('❌ Error al eliminar médico', 'danger')
    
    return redirect(url_for('mysql_listar_medicos'))

# ---------- CRUD PARA TURNOS ----------

@app.route('/mysql/turnos')
def mysql_listar_turnos():
    """Listar todos los turnos con información relacionada"""
    db = get_db()
    query = """
        SELECT t.*, 
               p.nombre as paciente_nombre, p.apellido as paciente_apellido,
               m.nombre as medico_nombre, m.apellido as medico_apellido, m.especialidad
        FROM turnos t
        JOIN pacientes p ON t.paciente_id = p.id
        JOIN medicos m ON t.medico_id = m.id
        ORDER BY t.fecha DESC, t.hora DESC
    """
    turnos = db.fetch_all(query)
    return render_template('mysql_turnos.html', turnos=turnos)

@app.route('/mysql/turnos/nuevo', methods=['GET', 'POST'])
def mysql_nuevo_turno():
    """Insertar nuevo turno"""
    db = get_db()
    
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
        result = db.execute_query(query, datos)
        
        if result > 0:
            flash('✅ Turno insertado correctamente', 'success')
        else:
            flash('❌ Error al insertar turno', 'danger')
        
        return redirect(url_for('mysql_listar_turnos'))
    
    pacientes = db.fetch_all("SELECT id, cedula, nombre, apellido FROM pacientes ORDER BY apellido")
    medicos = db.fetch_all("SELECT id, nombre, apellido, especialidad FROM medicos ORDER BY apellido")
    
    return render_template('mysql_turno_form.html', 
                          pacientes=pacientes, 
                          medicos=medicos, 
                          accion='Nuevo Turno')

@app.route('/mysql/turnos/editar/<int:id>', methods=['GET', 'POST'])
def mysql_editar_turno(id):
    """Modificar turno"""
    db = get_db()
    
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
        result = db.execute_query(query, datos)
        
        if result > 0:
            flash('✅ Turno actualizado correctamente', 'success')
        else:
            flash('❌ Error al actualizar turno', 'danger')
        
        return redirect(url_for('mysql_listar_turnos'))
    
    turno = db.fetch_one("SELECT * FROM turnos WHERE id = %s", (id,))
    if not turno:
        flash('❌ Turno no encontrado', 'danger')
        return redirect(url_for('mysql_listar_turnos'))
    
    pacientes = db.fetch_all("SELECT id, cedula, nombre, apellido FROM pacientes ORDER BY apellido")
    medicos = db.fetch_all("SELECT id, nombre, apellido, especialidad FROM medicos ORDER BY apellido")
    
    return render_template('mysql_turno_form.html', 
                          turno=turno,
                          pacientes=pacientes, 
                          medicos=medicos, 
                          accion='Editar Turno')

@app.route('/mysql/turnos/eliminar/<int:id>')
def mysql_eliminar_turno(id):
    """Eliminar turno"""
    db = get_db()
    result = db.execute_query("DELETE FROM turnos WHERE id = %s", (id,))
    
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