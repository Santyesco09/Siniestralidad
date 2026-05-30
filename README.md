# Siniestralidad
📋 Detalle de las Fases y Cambios Realizados
🧹 Fase 1: Limpieza y Preparación de Datos (fase1_limpieza.py)
    ¿Qué hace?
    Toma los archivos originales de accidentalidad, filtra el alcance exclusivo para los años requeridos (2020 y 2025) y procesa las inconsistencias del texto, nulos y tipos de datos.

    Cambios y Ajustes Críticos Aplicados:

    Filtrado Temporal: Se restringió el dataset para procesar únicamente los registros de los años 2020 y 2025.

    Tratamiento de Coordenadas: Se normalizaron los campos LATITUD y LONGITUD convirtiéndolos a cadenas de texto homogéneas para evitar pérdidas de precisión decimal o fallos por datos corruptos de origen.

    Manejo de Nulos: Se limpiaron las columnas de texto con valores vacíos asignando etiquetas estándar (ej. "Sin información") para prevenir excepciones de restricción en la base de datos.

    Estructuración Dimensional: Se pre-procesaron y exportaron 5 archivos CSV limpios listos para el esquema estrella (dim_actor.csv, dim_causa.csv, dim_vehiculo.csv, dim_via.csv y fact_accidente.csv).

📐 Fase 2: Modelado Dimensional (fase2_velocidad.sql)
    ¿Qué hace?
    Define la estructura del Data Warehouse en la base de datos Oracle mediante un Esquema en Estrella. Está compuesto por 4 tablas de dimensiones y 1 tabla de hechos central.

    Cambios y Ajustes Críticos Aplicados:

    Unificación de Llaves Relacionales: Se cambiaron los tipos de datos numéricos (NUMBER) e identificadores cortos de las llaves primarias (PRIMARY KEY) y foráneas (FOREIGN KEY) a un tipo estándar uniforme VARCHAR2(50). Esto eliminó de forma definitiva el error de incompatibilidad de tipos de Oracle (ORA-02267).

    Robustez en Longitudes: Se ampliaron las longitudes de campos descriptivos (como nombres de causas o direcciones) a VARCHAR2(250) o superiores para soportar strings extensos sin desbordar la memoria de las columnas.

    Integridad Referencial Segura: Se añadieron restricciones CASCADE CONSTRAINTS a los comandos DROP TABLE iniciales, permitiendo reiniciar el modelo de manera segura y automática sin bloqueos por llaves foráneas activas.

🚀 Fase 3: Automatización de Carga Masiva (fase3_insercion.py)
    ¿Qué hace?
    Es el pipeline programático encargado de leer de manera secuencial los archivos CSV limpios generados en la Fase 1 e inyectarlos de forma masiva en las tablas estructuradas de Oracle de la Fase 2.

    Cambios y Ajustes Críticos Aplicados:

    Actualización del Driver de Conexión: Se migró la cadena de conexión clásica al nuevo estándar de comunicación nativa oracle+oracledb, garantizando compatibilidad absoluta con entornos modernos de Python 3.14 sin depender de librerías obsoletas ni configuraciones de clientes pesados.

    Soporte de Tipado en Bloque (Mapeo Explicito): Se incorporó un diccionario de tipos (dtype) utilizando VARCHAR de SQLAlchemy exclusivo para la tabla de hechos FORMULARIO_ACCIDENTE. Esto forzó a Python a inyectar la latitud y longitud como texto plano, solucionando el error de precisión binaria decimal de Oracle (ArgumentError: FLOAT types use binary precision).

    Estética y Limpieza de Terminal: Se integró el módulo nativo warnings para silenciar las alertas amarillas de Pandas (UserWarning) referentes al uso de mayúsculas/minúsculas en los nombres de las tablas de Oracle, logrando un reporte de consola limpio, profesional y directo al grano.