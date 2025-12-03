USE sistema_reservas;

-- 1. Agregar campo teléfono a la tabla de usuarios
ALTER TABLE usuarios ADD COLUMN telefono VARCHAR(20) AFTER email;

-- 2. Insertar los nuevos recursos
INSERT INTO recursos (nombre, tipo, descripcion, estado) VALUES 
('Datashow Epson X41', 'equipo', 'Proyector HD para presentaciones', 'disponible'),
('Kit de Marcadores y Borrador', 'material', 'Set de 4 colores y borrador magnético', 'disponible'),
('Reglas y Juego Geometría', 'material', 'Juego completo para pizarra', 'disponible'),
('Aula 204 - Computo', 'laboratorio', 'Laboratorio con 20 PCs i7', 'disponible'),
('Aula 101 - General', 'sala', 'Aula teórica capacidad 30 personas', 'disponible');