import pandas as pd
import os
import warnings # 1. Configuración del manejo de alertas de Python

from sqlalchemy import create_engine
from sqlalchemy.types import VARCHAR

# Silenciar de forma absoluta cualquier tipo de UserWarning generado por Pandas o SQLAlchemy
warnings.filterwarnings("ignore", category=UserWarning)
warnings.simplefilter(action='ignore', category=UserWarning)

print("=======================================================")
print("===== FASE 3: AUTOMATIZACIÓN DE CARGA A ORACLE DB =====")
print("=======================================================")

# 1. Configuración de la cadena de conexión de Oracle
CONEXION_ORACLE = "oracle+oracledb://SYSTEM:Oracle2026*@localhost:1521/?service_name=XE"

try:
    engine = create_engine(CONEXION_ORACLE)
    print("-> Conexión exitosa al Data Warehouse de Oracle usando Thin Driver (oracledb).")
except Exception as e:
    print(f"❌ Error de conexión: {e}")
    exit()

CARPETA_DATOS = "CSV/datos_limpios"

# Mapeo de archivos CSV limpios a las tablas de la Fase 2 en Oracle
cargas = [
    ('dim_actor.csv', 'DIM_ACTOR_VIAL'),
    ('dim_causa.csv', 'DIM_CAUSA'),
    ('dim_vehiculo.csv', 'DIM_VEHICULO'),
    ('dim_via.csv', 'DIM_VIA'),
    ('fact_accidente.csv', 'FACT_ACCIDENTE') # Hechos siempre va al final
]

# Abrir una conexión con autocommit activado correctamente
with engine.connect().execution_options(autocommit=True) as conexion:

    for archivo, tabla_oracle in cargas:
        ruta_csv = os.path.join(CARPETA_DATOS, archivo)
        
        if os.path.exists(ruta_csv):
            print(f"\n📥 Cargando {archivo} en la tabla {tabla_oracle}...")
            df = pd.read_csv(ruta_csv, low_memory=False)
            
            dicitonario_tipos = {}
            if tabla_oracle == 'FACT_ACCIDENTE':
                df['LATITUD'] = df['LATITUD'].astype(str)
                df['LONGITUD'] = df['LONGITUD'].astype(str)
                dicitonario_tipos = {'LATITUD': VARCHAR(100), 'LONGITUD': VARCHAR(100)}
            
            df.to_sql(name=tabla_oracle, con=conexion, if_exists='append', index=False, dtype=dicitonario_tipos)
            
            conexion.commit()  # ← COMMIT explícito tras cada tabla
            print(f"✅ Éxito: {len(df)} registros insertados en {tabla_oracle}.")
        else:
            print(f"❌ Archivo no encontrado: {ruta_csv}")

print("\n--> ¡FASE 3 FINALIZADA! Data Warehouse totalmente poblado.")