# setup_mysql.py
# Script para crear la base de datos y tablas en MySQL

import mysql.connector
from mysql.connector import Error

def create_database_and_tables():
    """Crea la base de datos y las tablas necesarias"""
    
    # Configuración (ajusta según tu instalación)
    config = {
        'host': 'localhost',
        'user': 'root',
        'password': ''  # En XAMPP es vacío, en MySQL instalado pon tu contraseña
    }
    
    try:
        # Conectar sin base de datos específica
        conn = mysql.connector.connect(**config)
        cursor = conn.cursor()
        
        print("✅ Conectado a MySQL")
        
        # Crear base de datos
        cursor.execute("CREATE DATABASE IF NOT EXISTS turnos_db")
        print("✅ Base de datos 'turnos_db' creada/verificada")
        
        # Usar la base de datos
        cursor.execute("USE turnos_db")
        
        # ============================================
        # TABLA USUARIOS (requerida por la tarea)
        # ============================================
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS usuarios (
                id_usuario INT AUTO_INCREMENT PRIMARY KEY,
                nombre VARCHAR(100) NOT NULL,
                mail VARCHAR(100) UNIQUE NOT NULL,
                password VARCHAR(255) NOT NULL,
                fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("✅ Tabla 'usuarios' creada/verificada")
        
        # ============================================
        # TABLAS PARA EL SISTEMA DE TURNOS
        # ============================================
        
        # Tabla de pacientes
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS pacientes (
                id INT AUTO_INCREMENT PRIMARY KEY,
                cedula VARCHAR(10) UNIQUE NOT NULL,
                nombre VARCHAR(50) NOT NULL,
                apellido VARCHAR(50) NOT NULL,
                fecha_nacimiento DATE,
                telefono VARCHAR(15),
                direccion VARCHAR(200),
                email VARCHAR(100),
                fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("✅ Tabla 'pacientes' creada/verificada")
        
        # Tabla de médicos
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS medicos (
                id INT AUTO_INCREMENT PRIMARY KEY,
                cedula VARCHAR(10) UNIQUE NOT NULL,
                nombre VARCHAR(50) NOT NULL,
                apellido VARCHAR(50) NOT NULL,
                especialidad VARCHAR(50) NOT NULL,
                telefono VARCHAR(15),
                email VARCHAR(100),
                fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("✅ Tabla 'medicos' creada/verificada")
        
        # Tabla de turnos
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS turnos (
                id INT AUTO_INCREMENT PRIMARY KEY,
                paciente_id INT NOT NULL,
                medico_id INT NOT NULL,
                fecha DATE NOT NULL,
                hora TIME NOT NULL,
                motivo TEXT,
                estado ENUM('Programado', 'Confirmado', 'En curso', 'Completado', 'Cancelado', 'No asistió') DEFAULT 'Programado',
                fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (paciente_id) REFERENCES pacientes(id) ON DELETE CASCADE,
                FOREIGN KEY (medico_id) REFERENCES medicos(id) ON DELETE CASCADE
            )
        """)
        print("✅ Tabla 'turnos' creada/verificada")
        
        # ============================================
        # INSERTAR DATOS DE PRUEBA
        # ============================================
        
        # Verificar si hay datos
        cursor.execute("SELECT COUNT(*) FROM usuarios")
        if cursor.fetchone()[0] == 0:
            # Insertar usuario de prueba
            cursor.execute("""
                INSERT INTO usuarios (nombre, mail, password) 
                VALUES ('Admin', 'admin@patronato.gob.ec', '123456')
            """)
            print("✅ Usuario de prueba insertado")
        
        cursor.execute("SELECT COUNT(*) FROM medicos")
        if cursor.fetchone()[0] == 0:
            # Insertar médicos de prueba
            medicos = [
                ('1101234567', 'María', 'Rodríguez', 'Medicina General', '0991234567', 'maria@patronato.gob.ec'),
                ('1102345678', 'Juan', 'Pérez', 'Pediatría', '0992345678', 'juan@patronato.gob.ec'),
                ('1103456789', 'Ana', 'González', 'Ginecología', '0993456789', 'ana@patronato.gob.ec')
            ]
            cursor.executemany("""
                INSERT INTO medicos (cedula, nombre, apellido, especialidad, telefono, email)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, medicos)
            print("✅ Médicos de prueba insertados")
        
        conn.commit()
        print("\n🎉 ¡BASE DE DATOS CONFIGURADA EXITOSAMENTE!")
        
    except Error as e:
        print(f"❌ Error: {e}")
    
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()
            print("🔌 Conexión cerrada")

if __name__ == "__main__":
    create_database_and_tables()
