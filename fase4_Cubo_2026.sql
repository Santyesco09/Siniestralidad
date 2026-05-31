CREATE OR REPLACE VIEW V_CUBO_INFORMACION_ACCIDENTE_2020 AS
SELECT
    -- Fecha y Tiempo
    EXTRACT(YEAR FROM f_acc.FECHA_HORA_ACC) AS ANIO,
    'T' || TO_CHAR(f_acc.FECHA_HORA_ACC, 'Q') AS TRIMESTRE,
    TO_CHAR(f_acc.FECHA_HORA_ACC, 'Month', 'NLS_DATE_LANGUAGE = SPANISH') AS MES,
    f_acc.DIA_OCURRENCIA_ACC AS DIA_OCURRENCIA,
    f_acc.FECHA_HORA_ACC AS FECHA_HORA,

    -- Causa
    dm_causa.NOMBRE AS CAUSA_NOMBRE,
    
    -- Actor Vial
    dm_actor.CONDICION AS ACTOR_CONDICION,
    dm_actor.ESTADO AS ACTOR_ESTADO,
    dm_actor.EDAD AS ACTOR_EDAD,
    dm_actor.SEXO AS ACTOR_SEXO,
    
    -- Vehículo
    dm_vehiculo.CLASE AS VEHICULO_CLASE,
    
    -- Vía
    dm_via.SUPERFICIE AS VIA_SUPERFICIE,
    dm_via.ESTADO AS VIA_ESTADO,
    dm_via.CONDICIONES AS VIA_CONDICIONES,
    
    -- Medidas y KPIs
    COUNT(f_acc.FORMULARIO) OVER(PARTITION BY f_acc.LOCALIDAD, TO_CHAR(f_acc.FECHA_HORA_ACC, 'Q')) AS ACCIDENTES_POR_LOCALIDAD_TRIMESTRE,
    COUNT(f_acc.FORMULARIO) OVER(PARTITION BY dm_causa.ID_CAUSA) AS TOTAL_ACCIDENTES_POR_CAUSA,
    AVG(dm_actor.EDAD) OVER(PARTITION BY f_acc.LOCALIDAD) AS EDAD_PROMEDIO_LOCALIDAD,

    -- Clasificación Condicional
    CASE
        -- Gravedad crítica: Falla de infraestructura/vía + múltiples siniestros detectados
        WHEN dm_via.ESTADO IN ('MALO', 'EN REPARACION') AND dm_via.CONDICIONES = 'HUMEDA' THEN 'ALERTA: DESVIACIÓN CRÍTICA'
        
        -- Anomalías de comportamiento: Casos atípicos (ej: menores de edad en estados de embriaguez o conduciendo vehículos pesados)
        WHEN (dm_actor.EDAD < 18 AND dm_actor.ESTADO = 'EMBRIAGUEZ')
             OR (dm_vehiculo.CLASE IN ('TRACTOCAMION', 'BUS') AND dm_actor.EDAD < 20) THEN 'POSIBLE ANOMALÍA'
        
        -- Estado por defecto
        ELSE 'OPERACIÓN NORMAL'
    END AS DIAGNOSTICO_OPERATIVO
    
FROM FACT_ACCIDENTE f_acc

JOIN DIM_ACTOR_VIAL dm_actor ON f_acc.ID_ACCIDENTADO = dm_actor.ID_ACCIDENTADO
JOIN DIM_CAUSA dm_causa ON f_acc.ID_CAUSA = dm_causa.ID_CAUSA
JOIN DIM_VEHICULO dim_vehiculo ON f_acc.ID_PLACA = dim_vehiculo.ID_PLACA
JOIN DIM_VIA dim_via ON f_acc.ID_VIA = dim_via.ID_VIA

WHERE TO_CHAR(f_acc.FECHA_HORA_ACC, 'YYYY') = '2026';

-- SELECT * FROM V_CUBO_INFORMACION_ACCIDENTE_2020;

SELECT ESTADO, COUNT(*) AS DIM_VIA;
SELECT CONDICIONES, COUNT(*) AS DIM_VIA;

SELECT EDAD, ESTADO, COUNT(*) AS DIM_ACTOR_VIAL;

SELECT CLASE, COUNT(*) AS DIM_VEHICULO;