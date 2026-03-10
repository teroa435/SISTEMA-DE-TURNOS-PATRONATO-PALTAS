# setup_mysql.py
# Script para crear tablas en MySQL con XAMPP

import mysql.connector
from mysql.connector import Error

def create_tables():
    """Crea las tablas en la base de datos existente"""
    
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
        
        # ============================================
        # INSERTAR DATOS DE PRUEBA
        # ============================================
        
        # Verificar si hay datos en usuarios
        cursor.execute("SELECT COUNT(*) FROM usuarios")
        if cursor.fetchone()[0] == 0:
            # Insertar usuario de prueba
            cursor.execute("""
                INSERT INTO usuarios (nombre, mail, password) 
                VALUES 
                ('Admin', 'admin@patronato.gob.ec', '123456'),
                ('Usuario1', 'user1@patronato.gob.ec', 'password1'),
                ('Usuario2', 'user2@patronato.gob.ec', 'password2')
            """)
            print("✅ Usuarios de prueba insertados")
        
        # Verificar si hay datos en medicos
        cursor.execute("SELECT COUNT(*) FROM medicos")
        if cursor.fetchone()[0] == 0:
            # Insertar médicos de prueba
            medicos = [
                ('1101234567', 'María', 'Rodríguez', 'Medicina General', '0991234567', 'maria@patronato.gob.ec'),
                ('1102345678', 'Juan', 'Pérez', 'Pediatría', '0992345678', 'juan@patronato.gob.ec'),
                ('1103456789', 'Ana', 'González', 'Ginecología', '0993456789', 'ana@patronato.gob.ec'),
                ('1104567890', 'Carlos', 'Mendoza', 'Odontología', '0994567890', 'carlos@patronato.gob.ec')
            ]
            cursor.executemany("""
                INSERT INTO medicos (cedula, nombre, apellido, especialidad, telefono, email)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, medicos)
            print("✅ Médicos de prueba insertados")
        
        # Verificar si hay datos en pacientes
        cursor.execute("SELECT COUNT(*) FROM pacientes")
        if cursor.fetchone()[0] == 0:
            # Insertar pacientes de prueba
            pacientes = [
                ('1101122334', 'Pedro', 'Ramírez', '1980-05-15', '0991122334', 'Calle 10 de Agosto', 'pedro@email.com'),
                ('1102233445', 'Mariana', 'López', '1992-08-22', '0992233445', 'Av. Universitaria', 'mariana@email.com'),
                ('1103344556', 'José', 'Mendoza', '1975-03-10', '0993344556', 'Calle Bolívar', 'jose@email.com')
            ]
            cursor.executemany("""
                INSERT INTO pacientes (cedula, nombre, apellido, fecha_nacimiento, telefono, direccion, email)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, pacientes)
            print("✅ Pacientes de prueba insertados")
        
        conn.commit()
        
        # Mostrar resumen
        cursor.execute("SELECT COUNT(*) FROM usuarios")
        total_usuarios = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM medicos")
        total_medicos = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM pacientes")
        total_pacientes = cursor.fetchone()[0]
        
        print("\n" + "="*50)
        print("📊 RESUMEN DE LA BASE DE DATOS")
        print("="*50)
        print(f"👥 Usuarios: {total_usuarios}")
        print(f"👨‍⚕️ Médicos: {total_medicos}")
        print(f"👤 Pacientes: {total_pacientes}")
        print("="*50)
        print("\n🎉 ¡BASE DE DATOS CONFIGURADA EXITOSAMENTE!")
        
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
