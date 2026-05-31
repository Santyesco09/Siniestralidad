CREATE OR REPLACE VIEW V_CUBO_INFORMACION_ACCIDENTE_2020 AS
SELECT
    -- Dimensiones (Atributos para filtrar/agrupar)
    f_acc.FORMULARIO, -- Información básica del accidente
    dm_causa.NOMBRE,
    f_acc.FECHA_HORA_ACC AS FECHA_HORA,
    TO_CHAR(f_acc.FECHA_HORA_ACC, 'Month') as MES,
    f_acc.DIA_OCURRENCIA_ACC AS DIA_OCURRENCIA,

    dm_actor.CONDICION, -- Información del actor vial
    dm_actor.ESTADO,
    dm_actor.EDAD,
    dm_actor.SEXO,

    dm_vehiculo.CLASE, -- Información del vehículo

    f_acc.LOCALIDAD, -- Información geográfica y vial
    f_acc.BARRIO,
    dm_via.SUPERFICIE,
    dm_via.ESTADO,
    dm_via.CONDICIONES,
    f_acc.LATITUD,
    f_acc.LONGITUD,
    
    -- Medida Calculada (Indicador de Gestión)
    
FROM FACT_ACCIDENTE f_acc

WHERE TO_CHAR(f_acc.FECHA_HORA_ACC, 'YYYY') = '2020'

JOIN DIM_ACTOR_VIAL dm_actor ON f_acc.ID_ACCIDENTADO = dm_actor.ID_ACCIDENTADO
JOIN DIM_CAUSA dm_causa ON f_acc.ID_CAUSA = dm_causa.ID_CAUSA
JOIN DIM_VEHICULO dim_vehiculo ON f_acc.ID_PLACA = dim_vehiculo.ID_PLACA
JOIN DIM_VIA dim_via ON f_acc.ID_VIA = dim_via.ID_VIA;

-- SELECT * FROM V_CUBO_INFORMACION_ACCIDENTE_2020;