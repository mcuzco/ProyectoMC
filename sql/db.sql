CREATE DATABASE flaskcontact;
USE flaskcontact;

-- Tabla de Clientes
CREATE TABLE clientes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    telefono VARCHAR(20) NOT NULL
);

-- Tabla de Habitaciones
CREATE TABLE habitaciones (
    id INT AUTO_INCREMENT PRIMARY KEY,
    numero VARCHAR(50) NOT NULL,
    tipo VARCHAR(255) NOT NULL,
    precio DECIMAL(10, 2) NOT NULL
);

-- Tabla de Reservas
CREATE TABLE reservas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    cliente_id INT NOT NULL,
    habitacion_id INT NOT NULL,
    fecha_inicio DATE NOT NULL,
    fecha_fin DATE NOT NULL,
    FOREIGN KEY (cliente_id) REFERENCES clientes(id) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (habitacion_id) REFERENCES habitaciones(id) ON DELETE CASCADE ON UPDATE CASCADE
);

-- Tabla de Servicios
CREATE TABLE servicios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(255) NOT NULL,
    descripcion TEXT NOT NULL,
    precio DECIMAL(10, 2) NOT NULL
);

-- Tabla de Detalle de Reservas
CREATE TABLE detalle_reservas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    reserva_id INT NOT NULL,
    servicio_id INT NOT NULL,
    FOREIGN KEY (reserva_id) REFERENCES reservas(id) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (servicio_id) REFERENCES servicios(id) ON DELETE CASCADE ON UPDATE CASCADE
);

-- Tabla de Sucursales
CREATE TABLE sucursales (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(255) NOT NULL,
    direccion TEXT NOT NULL,
    telefono VARCHAR(20) NOT NULL
);

-- Tabla de Facturas
CREATE TABLE facturas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    reserva_id INT NOT NULL,
    fecha_emision DATE NOT NULL,
    total DECIMAL(10, 2) NOT NULL,
    FOREIGN KEY (reserva_id) REFERENCES reservas(id) ON DELETE CASCADE ON UPDATE CASCADE
);

-- Tabla de Informes
CREATE TABLE informes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    tipo VARCHAR(50) NOT NULL,
    descripcion TEXT,
    fecha DATE NOT NULL,
    total DECIMAL(10, 2),
    cliente_id INT,
    reserva_id INT,
    sucursal_id INT,
    FOREIGN KEY (cliente_id) REFERENCES clientes(id) ON DELETE SET NULL ON UPDATE CASCADE,
    FOREIGN KEY (reserva_id) REFERENCES reservas(id) ON DELETE SET NULL ON UPDATE CASCADE,
    FOREIGN KEY (sucursal_id) REFERENCES sucursales(id) ON DELETE SET NULL ON UPDATE CASCADE
);

-- ALTER TABLE para asegurar la integridad referencial
ALTER TABLE reservas
DROP FOREIGN KEY reservas_ibfk_1;

ALTER TABLE reservas
ADD CONSTRAINT reservas_ibfk_1
FOREIGN KEY (cliente_id) REFERENCES clientes(id)
ON DELETE CASCADE
ON UPDATE CASCADE;

ALTER TABLE detalle_reservas
DROP FOREIGN KEY detalle_reservas_ibfk_1;
ALTER TABLE detalle_reservas
DROP FOREIGN KEY detalle_reservas_ibfk_2;

ALTER TABLE detalle_reservas
ADD CONSTRAINT detalle_reservas_ibfk_1
FOREIGN KEY (reserva_id) REFERENCES reservas(id)
ON DELETE CASCADE
ON UPDATE CASCADE,
ADD CONSTRAINT detalle_reservas_ibfk_2
FOREIGN KEY (servicio_id) REFERENCES servicios(id)
ON DELETE CASCADE
ON UPDATE CASCADE;

ALTER TABLE facturas
DROP FOREIGN KEY facturas_ibfk_1;

ALTER TABLE facturas
ADD CONSTRAINT facturas_ibfk_1
FOREIGN KEY (reserva_id) REFERENCES reservas(id)
ON DELETE CASCADE
ON UPDATE CASCADE;

ALTER TABLE informes
DROP FOREIGN KEY informes_ibfk_1;
ALTER TABLE informes
DROP FOREIGN KEY informes_ibfk_2;
ALTER TABLE informes
DROP FOREIGN KEY informes_ibfk_3;

ALTER TABLE informes
ADD CONSTRAINT informes_ibfk_1
FOREIGN KEY (cliente_id) REFERENCES clientes(id)
ON DELETE SET NULL
ON UPDATE CASCADE,
ADD CONSTRAINT informes_ibfk_2
FOREIGN KEY (reserva_id) REFERENCES reservas(id)
ON DELETE SET NULL
ON UPDATE CASCADE,
ADD CONSTRAINT informes_ibfk_3
FOREIGN KEY (sucursal_id) REFERENCES sucursales(id)
ON DELETE SET NULL
ON UPDATE CASCADE;