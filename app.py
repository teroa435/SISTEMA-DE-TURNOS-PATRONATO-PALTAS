# app.py
# Aplicación Flask Principal - Patronato de Catacocha


# ============================================
# CRUD COMPLETO PARA MYSQL (Semana 13)
# ============================================
from Conexion.conexion import get_db, close_db
from flask import request, redirect, url_for, flash, render_template
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
# RUTAS DE LA APLICACIÓN WEB (de semanas anteriores)
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
    # Simulación de citas
    citas_ejemplo = [
        {'paciente': 'María González', 'fecha': '15/03/2024', 'servicio': 'Medicina General'},
        {'paciente': 'Juan Pérez', 'fecha': '16/03/2024', 'servicio': 'Odontología'},
        {'paciente': 'Ana Rodríguez', 'fecha': '17/03/2024', 'servicio': 'Trabajo Social'}
    ]
    return render_template('citas.html', citas=citas_ejemplo)

# ============================================
# NUEVAS RUTAS PARA PERSISTENCIA (Semana 12)
# ============================================

# ----- Gestión de Productos (SQLAlchemy) -----

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
        # Crear nuevo producto con SQLAlchemy
        producto = ProductoModel(
            nombre=form.nombre.data,
            descripcion=form.descripcion.data,
            precio=form.precio.data,
            cantidad=form.cantidad.data
        )
        
        # Guardar en base de datos
        db.session.add(producto)
        db.session.commit()
        
        # También guardar en archivos TXT, JSON, CSV
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

# ----- Ruta para ver todos los datos almacenados -----

@app.route('/datos')
def ver_datos():
    '''Muestra todos los datos almacenados en diferentes formatos'''
    
    # Leer datos de archivos
    datos_txt = txt_persistencia.leer()
    datos_json = json_persistencia.leer()
    datos_csv = csv_persistencia.leer()
    
    # Leer datos de SQLAlchemy
    productos_sql = ProductoModel.query.all()
    
    return render_template('datos.html', 
                          datos_txt=datos_txt,
                          datos_json=datos_json,
                          datos_csv=datos_csv,
                          productos_sql=productos_sql)

# ----- Rutas específicas para cada formato -----

@app.route('/guardar-txt', methods=['POST'])
def guardar_txt():
    '''Guarda datos en archivo TXT'''
    datos = request.form.get('datos', '')
    if datos:
        txt_persistencia.guardar(datos)
        flash('Datos guardados en TXT', 'success')
    return redirect(url_for('ver_datos'))

@app.route('/guardar-json', methods=['POST'])
def guardar_json():
    '''Guarda datos en archivo JSON'''
    try:
        datos = {
            'nombre': request.form.get('nombre', ''),
            'mensaje': request.form.get('mensaje', ''),
            'fecha': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        json_persistencia.guardar(datos)
        flash('Datos guardados en JSON', 'success')
    except Exception as e:
        flash(f'Error guardando en JSON: {e}', 'danger')
    return redirect(url_for('ver_datos'))

@app.route('/guardar-csv', methods=['POST'])
def guardar_csv():
    '''Guarda datos en archivo CSV'''
    try:
        datos = {
            'nombre': request.form.get('nombre', ''),
            'descripcion': request.form.get('descripcion', ''),
            'precio': float(request.form.get('precio', 0)),
            'cantidad': int(request.form.get('cantidad', 0))
        }
        csv_persistencia.guardar(datos)
        flash('Datos guardados en CSV', 'success')
    except Exception as e:
        flash(f'Error guardando en CSV: {e}', 'danger')
    return redirect(url_for('ver_datos'))

# ----- Ruta para probar SQLAlchemy directamente -----

@app.route('/productos/ejemplo')
def crear_producto_ejemplo():
    '''Crea un producto de ejemplo para probar'''
    producto = ProductoModel(
        nombre='Producto de Ejemplo',
        descripcion='Este es un producto creado para probar SQLAlchemy',
        precio=99.99,
        cantidad=10
    )
    db.session.add(producto)
    db.session.commit()
    
    flash('Producto de ejemplo creado', 'success')
    return redirect(url_for('productos'))

# ============================================
# INICIO DE LA APLICACIÓN
# ============================================

if __name__ == '__main__':
    app.run(debug=True)
