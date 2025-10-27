CREATE DATABASE IF NOT EXISTS sistema_reservas;
USE sistema_reservas;

-- ====================================================
-- 1️ TABLA: usuarios
-- ====================================================
CREATE TABLE usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    correo VARCHAR(100) UNIQUE NOT NULL,
    contraseña VARCHAR(255) NOT NULL,
    rol ENUM('usuario', 'admin') DEFAULT 'usuario'
);

-- ====================================================
-- 2️ TABLA: recursos
-- ====================================================
CREATE TABLE recursos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    tipo VARCHAR(50),
    descripcion TEXT,
    estado ENUM('disponible', 'no disponible') DEFAULT 'disponible'
);

-- ====================================================
-- 3️ TABLA: reservas
-- ====================================================
CREATE TABLE reservas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    usuario_id INT NOT NULL,
    recurso_id INT NOT NULL,
    fecha DATE NOT NULL,
    hora_inicio TIME NOT NULL,
    hora_fin TIME NOT NULL,
    estado ENUM('activa', 'cancelada') DEFAULT 'activa',
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE,
    FOREIGN KEY (recurso_id) REFERENCES recursos(id) ON DELETE CASCADE
);

-- ====================================================
-- 4️ TABLA: disponibilidad
-- ====================================================
CREATE TABLE disponibilidad (
    id INT AUTO_INCREMENT PRIMARY KEY,
    recurso_id INT NOT NULL,
    fecha DATE NOT NULL,
    hora_inicio TIME NOT NULL,
    hora_fin TIME NOT NULL,
    disponible BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (recurso_id) REFERENCES recursos(id) ON DELETE CASCADE
);

-- ====================================================
-- 5 TABLA: historial_reservas
-- ====================================================
CREATE TABLE historial_reservas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    reserva_id INT NOT NULL,
    usuario_id INT NOT NULL,
    recurso_id INT NOT NULL,
    fecha_reserva DATE NOT NULL,
    hora_inicio TIME NOT NULL,
    hora_fin TIME NOT NULL,
    accion VARCHAR(50) NOT NULL,
    FOREIGN KEY (reserva_id) REFERENCES reservas(id) ON DELETE CASCADE,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE,
    FOREIGN KEY (recurso_id) REFERENCES recursos(id) ON DELETE CASCADE
);
