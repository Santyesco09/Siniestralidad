import pandas as pd
import os
import warnings

from sqlalchemy import create_engine, text
from sqlalchemy.types import VARCHAR

# Silenciar advertencias de Pandas o SQLAlchemy
warnings.filterwarnings("ignore", category=UserWarning)
warnings.simplefilter(action='ignore', category=UserWarning)

print("=======================================================")
print("===== FASE 3: AUTOMATIZACIÓN DE CARGA A ORACLE DB =====")
print("=======================================================")

# 1. Configuración de la cadena de conexión de Oracle
CONEXION_ORACLE = "oracle+oracledb://SYSTEM:Oracle2026*@localhost:1521/?service_name=XE"

try:
    engine = create_engine(CONEXION_ORACLE)
    # Verificar la conexión con una consulta de prueba
    with engine.connect() as test_conn:
        test_conn.execute(text("SELECT 1 FROM DUAL"))
    print("-> Conexión exitosa al Data Warehouse de Oracle usando Thin Driver (oracledb).")
except Exception as e:
    print(f"❌ Error de conexión: {e}")
    exit()

CARPETA_DATOS = "CSV/datos_limpios"

# Mapeo de archivos CSV limpios a las tablas de la Fase 2 en Oracle
# IMPORTANTE: Las dimensiones SIEMPRE van antes que la tabla de hechos
# para respetar las restricciones de Foreign Key
cargas = [
    ('dim_actor.csv',    'DIM_ACTOR_VIAL'),
    ('dim_causa.csv',    'DIM_CAUSA'),
    ('dim_vehiculo.csv', 'DIM_VEHICULO'),
    ('dim_via.csv',      'DIM_VIA'),
    ('fact_accidente.csv', 'FACT_ACCIDENTE')
]

# CORRECCIÓN CLAVE PARA SQLALCHEMY 2.x:
# - engine.begin() abre una transacción real y hace COMMIT automático al salir del bloque 'with'
# - Si ocurre cualquier excepción, hace ROLLBACK automático para proteger la integridad
# - engine.connect() con execution_options(autocommit=True) fue ELIMINADO en SQLAlchemy 2.x
with engine.begin() as conexion:

    for archivo, tabla_oracle in cargas:
        ruta_csv = os.path.join(CARPETA_DATOS, archivo)

        if os.path.exists(ruta_csv):
            print(f"\n📥 Cargando {archivo} en la tabla {tabla_oracle}...")

            try:
                df = pd.read_csv(ruta_csv, low_memory=False)

                # Ajuste exclusivo para la tabla de hechos:
                # Forzar LATITUD y LONGITUD a VARCHAR para evitar choques de precisión float con Oracle
                dicitonario_tipos = {}
                if tabla_oracle == 'FACT_ACCIDENTE':
                    df['LATITUD']  = df['LATITUD'].astype(str)
                    df['LONGITUD'] = df['LONGITUD'].astype(str)
                    dicitonario_tipos = {
                        'LATITUD':  VARCHAR(100),
                        'LONGITUD': VARCHAR(100)
                    }

                # if_exists='append' respeta el DDL y las FK de la Fase 2
                # index=False evita crear una columna extra con el índice de Pandas
                df.to_sql(
                    name=tabla_oracle,
                    con=conexion,
                    if_exists='append',
                    index=False,
                    dtype=dicitonario_tipos
                )

                print(f"✅ Éxito: {len(df)} registros insertados en {tabla_oracle}.")

            except Exception as e:
                print(f"❌ Error al insertar en {tabla_oracle}: {e}")
                raise  # Re-lanzar para que engine.begin() haga ROLLBACK y proteja la BD

        else:
            print(f"❌ Archivo no encontrado: {ruta_csv}")

print("\n--> ¡FASE 3 FINALIZADA! Data Warehouse totalmente poblado.")