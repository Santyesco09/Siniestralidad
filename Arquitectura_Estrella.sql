-- Realizar de nuevo la creación de las tablas para asegurar que estén limpias y sin datos previos
DROP TABLE VM_ACC_ACTOR_VIAL;
DROP TABLE VM_ACC_CAUSA;
DROP TABLE VM_ACC_VEHICULO;
DROP TABLE VM_ACC_VIA;
DROP TABLE FORMULARIO_ACCIDENTE;

DELETE FROM FACT_VIAJE;
COMMIT;

-- 1. Dimensión de Actor vial
CREATE TABLE VM_ACC_ACTOR_VIAL (
    ID_ACCIDENTADO VARCHAR2(20) PRIMARY KEY, -- Llave primaria única para cada actor vial
    CONDICION VARCHAR2(4000), -- Condición del actor vial (e.g., conductor, peatón, pasajero)
    ESTADO VARCHAR2(4000), -- Estado del actor vial (e.g., vivo, muerto, herido)
    MUERTE_POSTERIOR VARCHAR2(4), --- Realizar limpieza N = True, S = False, null = Sin información
    EDAD NUMBER, -- Edad del actor vial (Hay que hacer limpieza de datos)
    GENERO VARCHAR2(15) -- Género del actor vial (Hay que hacer limpieza de datos)
);

-- 2. Dimensión de Causa
CREATE TABLE VM_ACC_CAUSA (
    ID_CAUSA NUMBER PRIMARY KEY, -- Llave primaria única para cada causa
    NOMBRE VARCHAR2(80) -- Descripción de la causa
);

-- 3. Dimensión de Vehículo
CREATE TABLE VM_ACC_VEHICULO (
    ID_PLACA VARCHAR2(15) PRIMARY KEY, -- Llave primaria única para cada vehículo
    CLASE VARCHAR2(30), -- Clase del vehículo (e.g., automóvil, motocicleta, camión)
    SERVICIO VARCHAR2(30) -- Servicio del vehículo (e.g., particular, público, oficial)
);

-- 4. Dimensión de Vía
CREATE TABLE VM_ACC_VIA (
    ID_VIA NUMBER PRIMARY KEY, -- Llave primaria única para cada vía
    SUPERFICIE VARCHAR2(200), -- Superficie de la vía (e.g., asfalto, tierra, adoquín)
    ESTADO VARCHAR2(200), -- Estado de la vía (e.g., buena, regular, mala)
    CONDICIONES VARCHAR2(200), -- Condiciones de la vía (e.g., seca, mojada, nevada)
    AGENTE VARCHAR2(2) -- Agente de la vía (e.g., S = Sí, N = No, null = Sin información)
);

-- 5. Tabla de Accidentes (El corazón de la estrella)
CREATE TABLE FORMULARIO_ACCIDENTE (
    FORMULARIO VARCHAR2(15) PRIMARY KEY,
    ID_ACCIDENTADO VARCHAR2(20),
    ID_CAUSA NUMBER,
    ID_PLACA VARCHAR2(15),
    ID_VIA NUMBER,

    FECHA_HORA_ACC DATE,
    DIA_OCURRENCIA_ACC VARCHAR2(9),
    DIRECCION VARCHAR2(100),
    GRAVEDAD VARCHAR2(20),
    CLASE_ACC VARCHAR2(20),
    LOCALIDAD VARCHAR2(50),
    LATITUD NUMBER,
    LONGITUD NUMBER,
    BARRIO VARCHAR2(255),

    CONSTRAINT FK_ACTOR_VIAL FOREIGN KEY (ID_ACCIDENTADO) REFERENCES VM_ACC_ACTOR_VIAL(ID_ACCIDENTADO),
    CONSTRAINT FK_CAUSA FOREIGN KEY (ID_CAUSA) REFERENCES VM_ACC_CAUSA(ID_CAUSA),
    CONSTRAINT FK_VEHICULO FOREIGN KEY (ID_PLACA) REFERENCES VM_ACC_VEHICULO(ID_PLACA),
    CONSTRAINT FK_VIA FOREIGN KEY (ID_VIA) REFERENCES VM_ACC_VIA(ID_VIA)
);

COMMIT;