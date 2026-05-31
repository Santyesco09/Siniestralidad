/*
-- ===========================================================================
-- FASE 2: MODELO EN ESTRELLA OPTIMIZADO (DDL)
-- ===========================================================================

1. LIMPIEZA DE AMBIENTE 
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
*/

-- 2. DIMENSIÓN DE ACTOR VIAL
CREATE TABLE DIM_ACTOR_VIAL (
    ID_ACCIDENTADO   VARCHAR2(50) PRIMARY KEY, -- Llave natural (Formulario)
    CONDICION        VARCHAR2(4000),           -- Conductor, Peatón, Pasajero, etc.
    ESTADO           VARCHAR2(4000),           -- Vivo, Muerto, Herido
    MUERTE_POSTERIOR VARCHAR2(20),             -- Ajustado a 20 para soportar "SIN DATA" / "NO REGISTRA"
    EDAD             NUMBER,                   -- NUMBER para permitir cálculos matemáticos (AVG)
    GENERO           VARCHAR2(50)              -- Ajustado a 50 para evitar truncados en contingencias del ETL
);

-- 3. DIMENSIÓN DE CAUSA (Validado)
CREATE TABLE DIM_CAUSA (
    ID_CAUSA     VARCHAR2(50) PRIMARY KEY,     -- Llave natural (Formulario)
    CODIGO_CAUSA VARCHAR2(50),
    NOMBRE       VARCHAR2(250)                 -- Espacio suficiente para descripción de hipótesis viales
);

-- 4. DIMENSIÓN DE VEHÍCULO (Validado)
CREATE TABLE DIM_VEHICULO (
    ID_PLACA VARCHAR2(50) PRIMARY KEY,         -- Llave natural (Formulario)
    PLACA_ID VARCHAR2(50),                     -- Almacena la placa alfanumérica original
    CLASE    VARCHAR2(100),                    -- Automóvil, Motocicleta, Camión
    SERVICIO VARCHAR2(100)                     -- Particular, Público, Oficial
);

-- 5. DIMENSIÓN DE VÍA (Validado)
CREATE TABLE DIM_VIA (
    ID_VIA      VARCHAR2(50) PRIMARY KEY,      -- Llave natural (Formulario)
    CODIGO_VIA  VARCHAR2(50),
    SUPERFICIE  VARCHAR2(200),                 -- Asfalto, Tierra, Adoquín
    ESTADO      VARCHAR2(200),                 -- Buena, Regular, Mala
    CONDICIONES VARCHAR2(200),                 -- Seca, Mojada, Con niebla
    AGENTE      VARCHAR2(20)                   -- Ajustado a 20 por seguridad de strings del ETL
);

-- 6. TABLA DE HECHOS (Mapeo relacional de integridad)
CREATE TABLE FACT_ACCIDENTE (
    FORMULARIO          VARCHAR2(50) PRIMARY KEY, -- Llave primaria del hecho
    ID_ACCIDENTADO      VARCHAR2(50),
    ID_CAUSA            VARCHAR2(50),
    ID_PLACA            VARCHAR2(50),
    ID_VIA              VARCHAR2(50),
    
    -- Atributos de explotación analítica
    FECHA_HORA_ACC      DATE,                     -- Tipo temporal nativo para jerarquías BI
    DIA_OCURRENCIA_ACC  VARCHAR2(50),
    DIRECCION           VARCHAR2(250),
    GRAVEDAD            VARCHAR2(100),
    CLASE_ACC           VARCHAR2(100),
    LOCALIDAD           VARCHAR2(150),
    LATITUD             VARCHAR2(100),            -- VARCHAR2 evita problemas de redondeo float de SQLAlchemy
    LONGITUD            VARCHAR2(100),            -- VARCHAR2 evita problemas de redondeo float de SQLAlchemy
    BARRIO              VARCHAR2(250),

    -- Restricciones de Llaves Foráneas Estrictas
    CONSTRAINT FK_ESTRELLA_ACTOR FOREIGN KEY (ID_ACCIDENTADO) REFERENCES DIM_ACTOR_VIAL(ID_ACCIDENTADO),
    CONSTRAINT FK_ESTRELLA_CAUSA FOREIGN KEY (ID_CAUSA) REFERENCES DIM_CAUSA(ID_CAUSA),
    CONSTRAINT FK_ESTRELLA_VEHICULO FOREIGN KEY (ID_PLACA) REFERENCES DIM_VEHICULO(ID_PLACA),
    CONSTRAINT FK_ESTRELLA_VIA FOREIGN KEY (ID_VIA) REFERENCES DIM_VIA(ID_VIA)
);

COMMIT;