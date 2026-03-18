# setup_mysql.py
# Script para crear tablas en MySQL con XAMPP (sin datos de prueba)

import mysql.connector
from mysql.connector import Error

def create_tables():
    \"\"\"Crea las tablas en la base de datos existente (sin datos de prueba)\"\"\"
    
    # Configuración para XAMPP
    config = {
        'host': '127.0.0.1',
        'user': 'root',
        'password': '',
        'database': 'turnos_db',
        'port': 3306
    }
    
    try:
        # Conectar directamente a la base de datos
        conn = mysql.connector.connect(**config)
        cursor = conn.cursor()
        
        print("✅ Conectado a MySQL (XAMPP)")
        print(f"📁 Usando base de datos: turnos_db")
        
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
        
        # NO INSERTAR DATOS DE PRUEBA - SOLO CREAR TABLAS
        
        conn.commit()
        
        print("\n" + "="*50)
        print("📊 TABLAS CREADAS CORRECTAMENTE")
        print("="*50)
        print("✅ usuarios")
        print("✅ pacientes")  
        print("✅ medicos")
        print("✅ turnos")
        print("="*50)
        print("\n🎉 ¡BASE DE DATOS CONFIGURADA EXITOSAMENTE!")
        print("💡 Los usuarios se crearán cuando se registren en la aplicación")
        
    except Error as e:
        print(f"❌ Error: {e}")
        print("\n💡 VERIFICA:")
        print("   1. Que XAMPP esté corriendo (MySQL iniciado)")
        print("   2. Que la base de datos 'turnos_db' exista en HeidiSQL")
        print("   3. Credenciales: usuario 'root', contraseña vacía")
        print("   4. Puerto: 3306")
    
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()
            print("🔌 Conexión cerrada")

if __name__ == "__main__":
    print("="*50)
    print("🚀 CONFIGURANDO BASE DE DATOS MYSQL (XAMPP)")
    print("="*50)
    create_tables()
