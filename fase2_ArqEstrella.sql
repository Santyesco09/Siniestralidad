-- Realizar de nuevo la creación de las tablas para asegurar que estén limpias y sin datos previos
/*
DROP TABLE FACT_ACCIDENTE CASCADE CONSTRAINTS; 
DROP TABLE DIM_ACTOR_VIAL CASCADE CONSTRAINTS;
DROP TABLE DIM_CAUSA CASCADE CONSTRAINTS;
DROP TABLE DIM_VEHICULO CASCADE CONSTRAINTS;
DROP TABLE DIM_VIA CASCADE CONSTRAINTS;
COMMIT;

-- Vaciar las tablas para evitar registros duplicados antes de volver a cargar con Python
TRUNCATE TABLE FACT_ACCIDENTE;
TRUNCATE TABLE DIM_ACTOR_VIAL;
TRUNCATE TABLE DIM_CAUSA;
TRUNCATE TABLE DIM_VEHICULO;
TRUNCATE TABLE DIM_VIA;

COMMIT;
*/

-- 1. Dimensión de Actor vial
CREATE TABLE DIM_ACTOR_VIAL (
    ID_ACCIDENTADO VARCHAR2(50) PRIMARY KEY, -- Llave primaria única para cada actor vial
    CONDICION VARCHAR2(4000), -- Condición del actor vial (e.g., conductor, peatón, pasajero)
    ESTADO VARCHAR2(4000), -- Estado del actor vial (e.g., vivo, muerto, herido)
    MUERTE_POSTERIOR VARCHAR2(4), --- Realizar limpieza N = True, S = False, null = Sin información
    EDAD VARCHAR2(50), -- Edad del actor vial (Hay que hacer limpieza de datos)
    GENERO VARCHAR2(15) -- Género del actor vial (Hay que hacer limpieza de datos)
);

-- 2. Dimensión de Causa
CREATE TABLE DIM_CAUSA (
    ID_CAUSA VARCHAR2(50) PRIMARY KEY, -- Llave primaria única para cada causa
    CODIGO_CAUSA VARCHAR2(50), -- Código original de la causa mapeado en el ETL
    NOMBRE VARCHAR2(250) -- Descripción de la causa
);

-- 3. Dimensión de Vehículo
CREATE TABLE DIM_VEHICULO (
    ID_PLACA VARCHAR2(50) PRIMARY KEY, -- Llave primaria única para cada vehículo
    PLACA_ID VARCHAR2(50), -- Placa real del vehículo mapeada en el ETL
    CLASE VARCHAR2(100), -- Clase del vehículo (e.g., automóvil, motocicleta, camión)
    SERVICIO VARCHAR2(100) -- Servicio del vehículo (e.g., particular, público, oficial)
);

-- 4. Dimensión de Vía
CREATE TABLE DIM_VIA (
    ID_VIA VARCHAR2(50) PRIMARY KEY, -- Llave primaria única para cada vía
    CODIGO_VIA VARCHAR2(50), -- Código original de la vía mapeado en el ETL
    SUPERFICIE VARCHAR2(200), -- Superficie de la vía (e.g., asfalto, tierra, adoquín)
    ESTADO VARCHAR2(200), -- Estado de la vía (e.g., buena, regular, mala)
    CONDICIONES VARCHAR2(200), -- Condiciones de la vía (e.g., seca, mojada, nevada)
    AGENTE VARCHAR2(10) -- Agente de la vía (e.g., S = Sí, N = No, null = Sin información)
);

-- 5. Tabla de Accidentes (El corazón de la estrella)
CREATE TABLE FACT_ACCIDENTE (
    FORMULARIO          VARCHAR2(50) PRIMARY KEY,
    ID_ACCIDENTADO      VARCHAR2(50),
    ID_CAUSA            VARCHAR2(50),
    ID_PLACA            VARCHAR2(50),
    ID_VIA              VARCHAR2(50),
    
    -- Campos descriptivos (Soportan texto para mayor flexibilidad en el ETL)
    FECHA_HORA_ACC      VARCHAR2(100),
    DIA_OCURRENCIA_ACC  VARCHAR2(50),
    DIRECCION           VARCHAR2(250),
    GRAVEDAD            VARCHAR2(100),
    CLASE_ACC           VARCHAR2(100),
    LOCALIDAD           VARCHAR2(150),
    LATITUD             VARCHAR2(100),
    LONGITUD            VARCHAR2(100),
    BARRIO              VARCHAR2(250),

    -- NUEVOS NOMBRES ÚNICOS PARA LAS LLAVES FORÁNEAS (Evita el ORA-02264)
    CONSTRAINT FK_ESTRELLA_ACTOR FOREIGN KEY (ID_ACCIDENTADO) REFERENCES DIM_ACTOR_VIAL(ID_ACCIDENTADO),
    CONSTRAINT FK_ESTRELLA_CAUSA FOREIGN KEY (ID_CAUSA) REFERENCES DIM_CAUSA(ID_CAUSA),
    CONSTRAINT FK_ESTRELLA_VEHICULO FOREIGN KEY (ID_PLACA) REFERENCES DIM_VEHICULO(ID_PLACA),
    CONSTRAINT FK_ESTRELLA_VIA FOREIGN KEY (ID_VIA) REFERENCES DIM_VIA(ID_VIA)
);

COMMIT;