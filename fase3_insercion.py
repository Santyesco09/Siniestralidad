import pandas as pd
import os
import warnings # 1. Configuración del manejo de alertas de Python

# Silenciar de forma absoluta cualquier tipo de UserWarning generado por Pandas o SQLAlchemy
warnings.filterwarnings("ignore", category=UserWarning)
warnings.simplefilter(action='ignore', category=UserWarning)

from sqlalchemy import create_engine
from sqlalchemy.types import VARCHAR

print("=======================================================")
print("=== FASE 3: AUTOMATIZACIÓN DE CARGA A ORACLE DB ======")
print("=======================================================")

# 1. Configuración de la cadena de conexión de Oracle
# NOTA: Cambiado a oracle+oracledb para total compatibilidad con Python 3.14
# Recuerda reemplazar 'SYSTEM' y 'tu_password' por tus credenciales de acceso reales
CONEXION_ORACLE = "oracle+oracledb://SYSTEM:Oracle2026*@localhost:1521/?service_name=XE"

try:
    engine = create_engine(CONEXION_ORACLE)
    print("-> Conexión exitosa al Data Warehouse de Oracle usando Thin Driver (oracledb).")
except Exception as e:
    print(f"❌ Error de conexión: {e}")
    exit()

CARPETA_DATOS = "datos_limpios"

# Mapeo de archivos CSV limpios a las tablas de la Fase 2 en Oracle
# NOTA: Se modificó 'FACT_ACCIDENTE' por 'FORMULARIO_ACCIDENTE' para acoplarse con tu SQL
cargas = [
    ('dim_actor.csv', 'VM_ACC_ACTOR_VIAL'),
    ('dim_causa.csv', 'VM_ACC_CAUSA'),
    ('dim_vehiculo.csv', 'VM_ACC_VEHICULO'),
    ('dim_via.csv', 'VM_ACC_VIA'),
    ('fact_accidente.csv', 'FORMULARIO_ACCIDENTE') # Hechos siempre va al final
]

for archivo, tabla_oracle in cargas:
    ruta_csv = os.path.join(CARPETA_DATOS, archivo)
    
    if os.path.exists(ruta_csv):
        print(f"\n📥 Cargando {archivo} en la tabla {tabla_oracle}...")
        df = pd.read_csv(ruta_csv, low_memory=False)
        
        # --- NUEVO AJUSTE EXCLUSIVO PARA LA TABLA DE HECHOS ---
        # Si estamos procesando la tabla de hechos, obligamos a mapear latitud y longitud como VARCHAR
        # Esto evita el choque de precisión binaria (FLOAT) con SQLAlchemy y Oracle
        dicitonario_tipos = {}
        if tabla_oracle == 'FORMULARIO_ACCIDENTE':
            # Convertimos las columnas del DataFrame a texto por seguridad en Pandas
            df['LATITUD'] = df['LATITUD'].astype(str)
            df['LONGITUD'] = df['LONGITUD'].astype(str)
            # Le indicamos a SQLAlchemy que las inyecte como VARCHAR en el motor
            dicitonario_tipos = {'LATITUD': VARCHAR(100), 'LONGITUD': VARCHAR(100)}
        
        # if_exists='append' inserta los datos respetando las estructuras de la Fase 2
        # index=False evita que se cree una columna extra con el índice de Pandas
        # dtype pasa las reglas de tipos especiales cuando existen (como con la latitud/longitud)
        df.to_sql(name=tabla_oracle, con=engine, if_exists='append', index=False, dtype=dicitonario_tipos)
        print(f"✅ Éxito: {len(df)} registros insertados en {tabla_oracle}.")
    else:
        print(f"❌ Archivo no encontrado: {ruta_csv}")

print("\n--> ¡FASE 3 FINALIZADA! Data Warehouse totalmente poblado.")