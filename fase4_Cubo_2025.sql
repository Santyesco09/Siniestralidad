/*
===========================================================================
 FASE 4: VISTA CUBO DE INFORMACIÓN DE ACCIDENTES 2025
===========================================================================
*/

CREATE OR REPLACE VIEW V_CUBO_ACCIDENTALIDAD_2025 AS
SELECT
    -- Jerarquía de Tiempo: Mes -> Dia (Corregido a TO_CHAR)
    TO_CHAR(f_acc.FECHA_ACC, 'MM') AS MES,
    f_acc.DIA_OCURRENCIA_ACC                                             AS DIA,
    
    -- Causa
    dm_causa.NOMBRE AS CAUSA,
    
    -- Actor Vial
    dm_actor.CONDICION AS ACTOR_CONDICION,
    dm_actor.ESTADO AS ACTOR_ESTADO,
    dm_actor.EDAD AS ACTOR_EDAD,
    dm_actor.GENERO AS ACTOR_SEXO, 
    
    -- Vehículo
    dim_vehiculo.CLASE AS VEHICULO_CLASE, 
    
    -- Vía
    dim_via.ESTADO AS VIA_ESTADO,
    dim_via.CONDICIONES AS VIA_CONDICIONES,

    -- Medidas y KPIs
    COUNT(f_acc.FORMULARIO)                  AS TOTAL_ACCIDENTES,
    AVG(dm_actor.EDAD)                       AS EDAD_PROMEDIO,
    
    SUM(CASE WHEN f_acc.GRAVEDAD = 'CON MUERTOS' THEN 1 ELSE 0 END) AS TOTAL_FATALIDADES,
    SUM(CASE WHEN f_acc.GRAVEDAD = 'CON HERIDOS' THEN 1 ELSE 0 END) AS TOTAL_HERIDOS,

    -- Clasificación condicional inteligencia de negocios
    CASE 
        -- Alerta Crítica: Accidentes fatales recurrentes o causas graves
        WHEN SUM(CASE WHEN f_acc.GRAVEDAD = 'CON MUERTOS' THEN 1 ELSE 0 END) > 0 
             OR COUNT(f_acc.FORMULARIO) >= 10 THEN 'ALERTA: DESVIACIÓN CRÍTICA'
        
        -- Posible Anomalía: Comportamiento inusual en la vía o volumen moderado
        WHEN COUNT(f_acc.FORMULARIO) BETWEEN 5 AND 9 THEN 'POSIBLE ANOMALÍA'
        
        -- Operación Regular Bajo Control
        ELSE 'OPERACIÓN NORMAL'
    END AS DIAGNOSTICO_OPERATIVO

FROM FACT_ACCIDENTE f_acc

JOIN DIM_ACTOR_VIAL dm_actor ON f_acc.ID_ACCIDENTADO = dm_actor.ID_ACCIDENTADO
JOIN DIM_CAUSA dm_causa ON f_acc.ID_CAUSA = dm_causa.ID_CAUSA
JOIN DIM_VEHICULO dim_vehiculo ON f_acc.ID_PLACA = dim_vehiculo.ID_PLACA
JOIN DIM_VIA dim_via ON f_acc.ID_VIA = dim_via.ID_VIA

WHERE TO_CHAR(f_acc.FECHA_ACC, 'YYYY') = '2025'

GROUP BY
    TO_CHAR(f_acc.FECHA_ACC, 'MM'),
    f_acc.DIA_OCURRENCIA_ACC,
    dm_causa.NOMBRE,
    dm_actor.CONDICION,
    dm_actor.ESTADO,
    dm_actor.EDAD,
    dm_actor.GENERO,
    dim_vehiculo.CLASE,
    dim_via.ESTADO,
    dim_via.CONDICIONES;

-- SELECT * FROM V_CUBO_ACCIDENTALIDAD_2025;