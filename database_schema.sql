-- ============================================
-- BASE DE DATOS DEL SISTEMA DE TURNOS
-- PATRONATO DE CATACOCHA
-- Semana 15: CRUD Completo y Reportes PDF
-- ============================================

-- Eliminar la base de datos si existe (opcional)
-- DROP DATABASE IF EXISTS turnos_db;

-- Crear la base de datos
CREATE DATABASE IF NOT EXISTS turnos_db;
USE turnos_db;

-- ============================================
-- 1. TABLA DE USUARIOS (Autenticación)
-- ============================================
CREATE TABLE IF NOT EXISTS usuarios (
    id_usuario INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    mail VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================
-- 2. TABLA DE PRODUCTOS (CRUD Principal)
-- ============================================
CREATE TABLE IF NOT EXISTS productos (
    id_producto INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    precio DECIMAL(10,2) NOT NULL DEFAULT 0,
    stock INT NOT NULL DEFAULT 0,
    descripcion TEXT,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================
-- 3. TABLA DE CLIENTES
-- ============================================
CREATE TABLE IF NOT EXISTS clientes (
    id_cliente INT AUTO_INCREMENT PRIMARY KEY,
    cedula VARCHAR(10) UNIQUE NOT NULL,
    nombre VARCHAR(50) NOT NULL,
    apellido VARCHAR(50) NOT NULL,
    telefono VARCHAR(15),
    email VARCHAR(100),
    direccion VARCHAR(200),
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================
-- 4. TABLA DE MÉDICOS
-- ============================================
CREATE TABLE IF NOT EXISTS medicos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    cedula VARCHAR(10) UNIQUE NOT NULL,
    nombre VARCHAR(50) NOT NULL,
    apellido VARCHAR(50) NOT NULL,
    especialidad VARCHAR(50) NOT NULL,
    telefono VARCHAR(15),
    email VARCHAR(100),
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================
-- 5. TABLA DE PACIENTES
-- ============================================
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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================
-- 6. TABLA DE TURNOS
-- ============================================
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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================
-- 7. TABLA DE FACTURAS
-- ============================================
CREATE TABLE IF NOT EXISTS facturas (
    id_factura INT AUTO_INCREMENT PRIMARY KEY,
    cliente_id INT NOT NULL,
    fecha DATE NOT NULL,
    total DECIMAL(10,2) NOT NULL DEFAULT 0,
    estado ENUM('Pendiente', 'Pagada', 'Cancelada') DEFAULT 'Pendiente',
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (cliente_id) REFERENCES clientes(id_cliente) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================
-- 8. TABLA DE DETALLE DE FACTURAS
-- ============================================
CREATE TABLE IF NOT EXISTS detalle_factura (
    id_detalle INT AUTO_INCREMENT PRIMARY KEY,
    factura_id INT NOT NULL,
    producto_id INT NOT NULL,
    cantidad INT NOT NULL,
    precio_unitario DECIMAL(10,2) NOT NULL,
    subtotal DECIMAL(10,2) NOT NULL,
    FOREIGN KEY (factura_id) REFERENCES facturas(id_factura) ON DELETE CASCADE,
    FOREIGN KEY (producto_id) REFERENCES productos(id_producto) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================
-- 9. ÍNDICES PARA OPTIMIZAR BÚSQUEDAS
-- ============================================
CREATE INDEX idx_usuarios_mail ON usuarios(mail);
CREATE INDEX idx_productos_nombre ON productos(nombre);
CREATE INDEX idx_clientes_cedula ON clientes(cedula);
CREATE INDEX idx_clientes_nombre ON clientes(nombre, apellido);
CREATE INDEX idx_medicos_especialidad ON medicos(especialidad);
CREATE INDEX idx_turnos_fecha ON turnos(fecha);
CREATE INDEX idx_turnos_estado ON turnos(estado);
CREATE INDEX idx_facturas_fecha ON facturas(fecha);
CREATE INDEX idx_facturas_estado ON facturas(estado);

-- ============================================
-- 10. DATOS DE PRUEBA (Opcional - Solo para desarrollo)
-- ============================================

-- Insertar usuarios de prueba (contraseñas encriptadas con werkzeug)
-- NOTA: En producción NO usar datos de prueba por defecto
-- Las contraseñas aquí son: '123456' encriptada con generate_password_hash
-- INSERT INTO usuarios (nombre, mail, password) VALUES 
-- ('Admin', 'admin@patronato.gob.ec', 'pbkdf2:sha256:600000$...'),
-- ('Usuario Test', 'test@ejemplo.com', 'pbkdf2:sha256:600000$...');

-- Insertar productos de prueba (opcional)
-- INSERT INTO productos (nombre, precio, stock, descripcion) VALUES
-- ('Paracetamol 500mg', 5.50, 100, 'Analgésico y antipirético'),
-- ('Ibuprofeno 400mg', 8.00, 80, 'Antiinflamatorio'),
-- ('Amoxicilina 500mg', 12.00, 50, 'Antibiótico'),
-- ('Vitamina C 1000mg', 15.00, 60, 'Suplemento vitamínico'),
-- ('Jarabe para la tos', 9.00, 40, 'Antitusivo');

-- Insertar médicos de prueba (opcional)
-- INSERT INTO medicos (cedula, nombre, apellido, especialidad, telefono, email) VALUES
-- ('1101234567', 'María', 'Rodríguez', 'Medicina General', '0991234567', 'maria@patronato.gob.ec'),
-- ('1102345678', 'Juan', 'Pérez', 'Pediatría', '0992345678', 'juan@patronato.gob.ec'),
-- ('1103456789', 'Ana', 'González', 'Ginecología', '0993456789', 'ana@patronato.gob.ec');

-- Insertar pacientes de prueba (opcional)
-- INSERT INTO pacientes (cedula, nombre, apellido, fecha_nacimiento, telefono, direccion, email) VALUES
-- ('1101122334', 'Pedro', 'Ramírez', '1980-05-15', '0991122334', 'Calle 10 de Agosto', 'pedro@email.com'),
-- ('1102233445', 'Mariana', 'López', '1992-08-22', '0992233445', 'Av. Universitaria', 'mariana@email.com'),
-- ('1103344556', 'José', 'Mendoza', '1975-03-10', '0993344556', 'Calle Bolívar', 'jose@email.com');

-- ============================================
-- 11. VISTAS ÚTILES
-- ============================================

-- Vista de turnos con información completa
CREATE OR REPLACE VIEW vista_turnos AS
SELECT 
    t.id,
    t.fecha,
    t.hora,
    t.motivo,
    t.estado,
    p.id as paciente_id,
    p.nombre as paciente_nombre,
    p.apellido as paciente_apellido,
    p.cedula as paciente_cedula,
    p.telefono as paciente_telefono,
    m.id as medico_id,
    m.nombre as medico_nombre,
    m.apellido as medico_apellido,
    m.especialidad
FROM turnos t
INNER JOIN pacientes p ON t.paciente_id = p.id
INNER JOIN medicos m ON t.medico_id = m.id
ORDER BY t.fecha DESC, t.hora DESC;

-- Vista de productos con stock bajo
CREATE OR REPLACE VIEW vista_productos_stock_bajo AS
SELECT * FROM productos WHERE stock < 10 ORDER BY stock ASC;

-- ============================================
-- 12. PROCEDIMIENTOS ALMACENADOS
-- ============================================

-- Procedimiento para obtener estadísticas
DELIMITER //
CREATE PROCEDURE sp_estadisticas_turnos()
BEGIN
    SELECT 
        COUNT(*) as total_turnos,
        SUM(CASE WHEN estado = 'Programado' THEN 1 ELSE 0 END) as programados,
        SUM(CASE WHEN estado = 'Confirmado' THEN 1 ELSE 0 END) as confirmados,
        SUM(CASE WHEN estado = 'Completado' THEN 1 ELSE 0 END) as completados,
        SUM(CASE WHEN estado = 'Cancelado' THEN 1 ELSE 0 END) as cancelados
    FROM turnos;
END //
DELIMITER ;

-- ============================================
-- 13. TRIGGERS
-- ============================================

-- Trigger para actualizar stock después de una factura
DELIMITER //
CREATE TRIGGER trg_actualizar_stock
AFTER INSERT ON detalle_factura
FOR EACH ROW
BEGIN
    UPDATE productos 
    SET stock = stock - NEW.cantidad 
    WHERE id_producto = NEW.producto_id;
END //
DELIMITER ;

-- ============================================
-- MOSTRAR TABLAS CREADAS
-- ============================================
SHOW TABLES;

-- ============================================
-- RESUMEN DE TABLAS
-- ============================================
SELECT '===========================================' AS '';
SELECT 'RESUMEN DE TABLAS CREADAS' AS '';
SELECT '===========================================' AS '';
SELECT '✅ usuarios - Tabla de autenticación' AS '';
SELECT '✅ productos - Tabla de productos (CRUD)' AS '';
SELECT '✅ clientes - Tabla de clientes' AS '';
SELECT '✅ medicos - Tabla de médicos' AS '';
SELECT '✅ pacientes - Tabla de pacientes' AS '';
SELECT '✅ turnos - Tabla de turnos' AS '';
SELECT '✅ facturas - Tabla de facturas' AS '';
SELECT '✅ detalle_factura - Detalle de facturas' AS '';
SELECT '===========================================' AS '';
SELECT '🎉 BASE DE DATOS CONFIGURADA EXITOSAMENTE' AS '';
SELECT '===========================================' AS '';