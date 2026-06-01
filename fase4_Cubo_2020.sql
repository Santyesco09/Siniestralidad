/*
===========================================================================
 FASE 4: VISTA CUBO DE INFORMACIÓN DE ACCIDENTES 2020 (CORREGIDA)
===========================================================================
*/

CREATE OR REPLACE VIEW V_CUBO_ACCIDENTALIDAD_2020 AS
SELECT
    -- 1. Jerarquía Temporal (Corregido uso de SUBSTR para campo VARCHAR2)
    TO_CHAR(f_acc.FECHA_ACC, 'MM')                                       AS MES,
    TO_CHAR(f_acc.FECHA_ACC, 'DD')                                       AS DIA,
    f_acc.DIA_OCURRENCIA_ACC                                             AS DIA_SEMANA,
    SUBSTR(f_acc.HORA_ACC, 1, 2)                                         AS HORA,
    
    -- 2. Dimensión Causa
    dm_causa.NOMBRE                                                      AS CAUSA,
    
    -- 3. Dimensión Actor Vial (Atributos Descriptivos)
    dm_actor.CONDICION                                                   AS ACTOR_CONDICION,
    dm_actor.ESTADO                                                      AS ACTOR_ESTADO,
    dm_actor.GENERO                                                      AS ACTOR_SEXO, 
    
    -- 4. Dimensión Vehículo (Atributo Descriptivo)
    dim_vehiculo.CLASE                                                   AS TIPO_ACCIDENTE, 
    
    -- 5. Dimensión Geográfica y Vía
    f_acc.LOCALIDAD,
    f_acc.BARRIO,
    dim_via.ESTADO                                                       AS VIA_ESTADO,
    dim_via.CONDICIONES                                                  AS VIA_CONDICIONES,
    f_acc.LATITUD,
    f_acc.LONGITUD,

    -- 6. MEDIDAS Y KPIs (Métricas Agregadas)
    COUNT(f_acc.FORMULARIO)                                              AS TOTAL_ACCIDENTES,
    ROUND(AVG(dm_actor.EDAD), 2)                                         AS EDAD_PROMEDIO,
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
    TO_CHAR(f_acc.FECHA_ACC, 'DD'),
    f_acc.DIA_OCURRENCIA_ACC,
    SUBSTR(f_acc.HORA_ACC, 1, 2),
    dm_causa.NOMBRE,
    dm_actor.CONDICION,
    dm_actor.ESTADO,
    dm_actor.GENERO,
    dim_vehiculo.CLASE,
    f_acc.LOCALIDAD,
    f_acc.BARRIO,
    dim_via.ESTADO,
    dim_via.CONDICIONES,
    f_acc.LATITUD,
    f_acc.LONGITUD;

-- SELECT * FROM V_CUBO_ACCIDENTALIDAD_2020;