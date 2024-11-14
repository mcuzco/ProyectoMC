CREATE DATABASE flaskcontact;
USE flaskcontact;

CREATE TABLE clientes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    telefono VARCHAR(20) NOT NULL
);

CREATE TABLE reservas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    cliente_id INT NOT NULL,
    fecha_inicio DATE NOT NULL,
    fecha_fin DATE NOT NULL,
    FOREIGN KEY (cliente_id) REFERENCES clientes(id) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE servicios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(255) NOT NULL,
    descripcion TEXT NOT NULL,
    precio DECIMAL(10, 2) NOT NULL
);

CREATE TABLE detalle_reservas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    reserva_id INT NOT NULL,
    servicio_id INT NOT NULL,
    FOREIGN KEY (reserva_id) REFERENCES reservas(id) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (servicio_id) REFERENCES servicios(id) ON DELETE CASCADE ON UPDATE CASCADE
);

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


-- Tabla para prueba de login 

CREATE TABLE usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL
);