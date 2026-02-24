# database.py
# Configuración de la base de datos SQLite para el Patronato de Catacocha

import sqlite3

def crear_base_datos():
    """Crea la base de datos y las tablas necesarias"""
    
    conn = sqlite3.connect('citas.db')
    cursor = conn.cursor()
    
    # Tabla de pacientes
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS pacientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cedula TEXT UNIQUE NOT NULL,
            nombre TEXT NOT NULL,
            apellido TEXT NOT NULL,
            fecha_nacimiento TEXT,
            telefono TEXT,
            direccion TEXT,
            email TEXT,
            fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Tabla de médicos
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS medicos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cedula TEXT UNIQUE NOT NULL,
            nombre TEXT NOT NULL,
            apellido TEXT NOT NULL,
            especialidad TEXT NOT NULL,
            telefono TEXT,
            email TEXT,
            fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Tabla de citas
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS citas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            paciente_id INTEGER NOT NULL,
            medico_id INTEGER NOT NULL,
            fecha TEXT NOT NULL,
            hora TEXT NOT NULL,
            motivo TEXT,
            estado TEXT DEFAULT 'Programada',
            fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (paciente_id) REFERENCES pacientes (id),
            FOREIGN KEY (medico_id) REFERENCES medicos (id)
        )
    ''')
    
    # Índices para búsquedas rápidas
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_citas_fecha ON citas(fecha)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_citas_paciente ON citas(paciente_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_citas_medico ON citas(medico_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_citas_estado ON citas(estado)')
    
    conn.commit()
    conn.close()
    
    print("✅ Base de datos creada/verificada exitosamente")

def insertar_datos_prueba():
    """Inserta datos de ejemplo para pruebas"""
    
    conn = sqlite3.connect('citas.db')
    cursor = conn.cursor()
    
    # Verificar si ya hay datos
    cursor.execute("SELECT COUNT(*) FROM medicos")
    if cursor.fetchone()[0] > 0:
        print("ℹ️ La base de datos ya tiene datos. Omitiendo inserción de prueba.")
        conn.close()
        return
    
    # Insertar médicos de ejemplo
    medicos_ejemplo = [
        ('1101234567', 'María', 'Rodríguez', 'Medicina General', '0991234567', 'maria.rodriguez@patronato.gob.ec'),
        ('1102345678', 'Juan', 'Pérez', 'Pediatría', '0992345678', 'juan.perez@patronato.gob.ec'),
        ('1103456789', 'Ana', 'González', 'Ginecología', '0993456789', 'ana.gonzalez@patronato.gob.ec'),
        ('1104567890', 'Carlos', 'Mendoza', 'Odontología', '0994567890', 'carlos.mendoza@patronato.gob.ec'),
        ('1105678901', 'Laura', 'Castillo', 'Trabajo Social', '0995678901', 'laura.castillo@patronato.gob.ec')
    ]
    
    cursor.executemany('''
        INSERT INTO medicos (cedula, nombre, apellido, especialidad, telefono, email)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', medicos_ejemplo)
    
    # Insertar pacientes de ejemplo
    pacientes_ejemplo = [
        ('1101122334', 'Pedro', 'Ramírez', '1980-05-15', '0991122334', 'Calle 10 de Agosto', 'pedro@email.com'),
        ('1102233445', 'Mariana', 'López', '1992-08-22', '0992233445', 'Av. Universitaria', 'mariana@email.com'),
        ('1103344556', 'José', 'Mendoza', '1975-03-10', '0993344556', 'Calle Bolívar', 'jose@email.com'),
        ('1104455667', 'Carmen', 'Vega', '1988-11-30', '0994455667', 'Calle Sucre', 'carmen@email.com'),
        ('1105566778', 'Luis', 'Torres', '1995-07-18', '0995566778', 'Av. 24 de Mayo', 'luis@email.com')
    ]
    
    cursor.executemany('''
        INSERT INTO pacientes (cedula, nombre, apellido, fecha_nacimiento, telefono, direccion, email)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', pacientes_ejemplo)
    
    # Insertar citas de ejemplo
    citas_ejemplo = [
        (1, 1, '2024-03-15', '09:00', 'Control anual', 'Confirmada'),
        (2, 2, '2024-03-15', '10:30', 'Vacunación', 'Programada'),
        (3, 3, '2024-03-16', '11:00', 'Consulta prenatal', 'Programada'),
        (4, 4, '2024-03-16', '15:00', 'Limpieza dental', 'Confirmada'),
        (5, 5, '2024-03-17', '08:30', 'Asesoría familiar', 'Programada')
    ]
    
    cursor.executemany('''
        INSERT INTO citas (paciente_id, medico_id, fecha, hora, motivo, estado)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', citas_ejemplo)
    
    conn.commit()
    conn.close()
    
    print("✅ Datos de prueba insertados exitosamente")

if __name__ == "__main__":
    crear_base_datos()
    insertar_datos_prueba()