CREATE DATABASE IF NOT EXISTS eduwit_go;
USE eduwit_go;

CREATE TABLE categorias (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    color VARCHAR(10) NOT NULL
);

CREATE TABLE programas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    categoria_id INT,
    nombre VARCHAR(100) NOT NULL,
    estado TINYINT(1) DEFAULT 1, 
    json_data JSON NOT NULL,  
    version VARCHAR(15) NOT NULL DEFAULT '010124.0000',  
    FOREIGN KEY (categoria_id) REFERENCES categorias(id)
);

INSERT INTO categorias (nombre, color) VALUES ('General', '#6c757d');