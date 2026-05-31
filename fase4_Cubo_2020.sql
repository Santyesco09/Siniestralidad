/*
===========================================================================
 FASE 4: VISTA CUBO DE INFORMACIÓN DE ACCIDENTES 2020
===========================================================================
*/

CREATE OR REPLACE VIEW V_CUBO_ACCIDENTALIDAD_2020 AS
SELECT
    -- 1. Jerarquía Temporal
    TO_CHAR(f_acc.FECHA_ACC, 'MM')                                       AS MES,
    f_acc.DIA_OCURRENCIA_ACC                                             AS DIA,
    
    -- 2. Dimensión Causa
    dm_causa.NOMBRE                                                      AS CAUSA,
    
    -- 3. Dimensión Actor Vial (Atributos Descriptivos)
    dm_actor.CONDICION                                                   AS ACTOR_CONDICION,
    dm_actor.ESTADO                                                      AS ACTOR_ESTADO,
    dm_actor.GENERO                                                      AS ACTOR_SEXO, 
    
    -- 4. Dimensión Vehículo (Atributo Descriptivo)
    dim_vehiculo.CLASE                                                   AS VEHICULO_CLASE, 
    
    -- 5. Dimensión Geográfica y Vía
    f_acc.LOCALIDAD,
    f_acc.BARRIO,
    dim_via.ESTADO                                                       AS VIA_ESTADO,
    dim_via.CONDICIONES                                                  AS VIA_CONDICIONES,
    f_acc.LATITUD,
    f_acc.LONGITUD,

    -- 6. MEDIDAS Y KPIs (Métricas Agregadas)
    COUNT(f_acc.FORMULARIO)                                              AS TOTAL_ACCIDENTES,
    ROUND(AVG(dm_actor.EDAD), 2)                                         AS EDAD_PROMEDIO, -- Removido dm_actor.EDAD como columna base
    SUM(CASE WHEN f_acc.GRAVEDAD = 'CON MUERTOS' THEN 1 ELSE 0 END)      AS TOTAL_FATALIDADES,
    SUM(CASE WHEN f_acc.GRAVEDAD = 'CON HERIDOS' THEN 1 ELSE 0 END)      AS TOTAL_HERIDOS,

    -- 7. Clasificación Condicional (Inteligencia de Negocios)
    CASE 
        WHEN SUM(CASE WHEN f_acc.GRAVEDAD = 'CON MUERTOS' THEN 1 ELSE 0 END) > 0 
             OR COUNT(f_acc.FORMULARIO) >= 10 THEN 'ALERTA: DESVIACIÓN CRÍTICA'
        WHEN COUNT(f_acc.FORMULARIO) BETWEEN 5 AND 9 THEN 'POSIBLE ANOMALÍA'
        ELSE 'OPERACIÓN NORMAL'
    END AS DIAGNOSTICO_OPERATIVO

FROM FACT_ACCIDENTE f_acc
INNER JOIN DIM_ACTOR_VIAL dm_actor   ON f_acc.ID_ACCIDENTADO = dm_actor.ID_ACCIDENTADO
INNER JOIN DIM_CAUSA dm_causa        ON f_acc.ID_CAUSA = dm_causa.ID_CAUSA
INNER JOIN DIM_VEHICULO dim_vehiculo ON f_acc.ID_PLACA = dim_vehiculo.ID_PLACA
INNER JOIN DIM_VIA dim_via           ON f_acc.ID_VIA = dim_via.ID_VIA

-- FILTRO CRÍTICO: Asegurar la partición histórica correcta del cubo
WHERE EXTRACT(YEAR FROM f_acc.FECHA_ACC) = 2020

GROUP BY 
    TO_CHAR(f_acc.FECHA_ACC, 'MM'),
    f_acc.DIA_OCURRENCIA_ACC,
    dm_causa.NOMBRE,
    dm_actor.CONDICION,
    dm_actor.ESTADO,
    dm_actor.GENERO,       -- Mapeo directo para evitar el NULL
    dim_vehiculo.CLASE,    -- Incluido de forma estricta
    f_acc.LOCALIDAD,
    f_acc.BARRIO,
    dim_via.ESTADO,        -- Incluido de forma estricta
    dim_via.CONDICIONES,   -- Incluido de forma estricta
    f_acc.LATITUD,
    f_acc.LONGITUD;

-- SELECT * FROM V_CUBO_ACCIDENTALIDAD_2020;