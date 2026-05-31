import pandas as pd
import os
import warnings

# Silenciar alertas de Pandas o SQLAlchemy para mantener la terminal limpia
warnings.filterwarnings("ignore", category=UserWarning)
warnings.simplefilter(action='ignore', category=UserWarning)

from sqlalchemy import create_engine, Date, Integer
from sqlalchemy.types import VARCHAR

print("=======================================================")
print("===== FASE 3: AUTOMATIZACIÓN DE CARGA A ORACLE DB =====")
print("=======================================================")

# Cadena de conexión a Oracle
CONEXION_ORACLE = "oracle+oracledb://SYSTEM:Oracle2026*@localhost:1521/?service_name=XEPDB1"

try:
    engine = create_engine(CONEXION_ORACLE)
    print("-> Conexión exitosa al Data Warehouse de Oracle usando Thin Driver (oracledb).")
except Exception as e:
    print(f"❌ Error de conexión: {e}")
    exit()

CARPETA_DATOS = "datos_limpios"

# MAPEADO CORRECTO: Apuntando estrictamente a FACT_ACCIDENTE
cargas = [
    ('dim_actor.csv', 'DIM_ACTOR_VIAL'),
    ('dim_causa.csv', 'DIM_CAUSA'),
    ('dim_vehiculo.csv', 'DIM_VEHICULO'),
    ('dim_via.csv', 'DIM_VIA'),
    ('fact_accidente.csv', 'FACT_ACCIDENTE') 
]

try:
    with engine.connect() as conexion_directa:
        for archivo, tabla_oracle in cargas:
            ruta_csv = os.path.join(CARPETA_DATOS, archivo)
            
            if os.path.exists(ruta_csv):
                print(f"\n📥 Cargando {archivo} en la tabla {tabla_oracle}...")
                
                # Inicializar mapeo de tipos específicos para SQLAlchemy
                diccionario_tipos = {}
                
                if tabla_oracle == 'DIM_ACTOR_VIAL':
                    df = pd.read_csv(ruta_csv, low_memory=False)
                    df['EDAD'] = pd.to_numeric(df['EDAD'], errors='coerce').astype('Int64')
                    diccionario_tipos = {'EDAD': Integer()}
                    
                elif tabla_oracle == 'FACT_ACCIDENTE':
                    df = pd.read_csv(ruta_csv, low_memory=False)
                    
                    # Convertir directamente la columna limpia a tipo fecha nativa de Oracle
                    df['FECHA_ACC'] = pd.to_datetime(df['FECHA_ACC'], format='%Y-%m-%d', errors='coerce')
                    
                    # Forzar campos de texto y georreferenciación planos para evitar truncados
                    df['HORA_ACC'] = df['HORA_ACC'].astype(str).str.strip()
                    df['LATITUD'] = df['LATITUD'].astype(str)
                    df['LONGITUD'] = df['LONGITUD'].astype(str)
                    
                    # Mapear explícitamente los tipos para SQLAlchemy
                    diccionario_tipos = {
                        'FORMULARIO': VARCHAR(100),
                        'ID_ACCIDENTADO': VARCHAR(100),
                        'ID_CAUSA': VARCHAR(100),
                        'ID_PLACA': VARCHAR(100),
                        'ID_VIA': VARCHAR(100),
                        'FECHA_ACC': Date(),
                        'HORA_ACC': VARCHAR(50),
                        'DIA_OCURRENCIA_ACC': VARCHAR(100),
                        'DIRECCION': VARCHAR(250),
                        'GRAVEDAD': VARCHAR(100),
                        'CLASE_ACC': VARCHAR(100),
                        'LOCALIDAD': VARCHAR(150),
                        'LATITUD': VARCHAR(100), 
                        'LONGITUD': VARCHAR(100),
                        'BARRIO': VARCHAR(250)
                    }
                else:
                    df = pd.read_csv(ruta_csv, low_memory=False, dtype=str)
                
                # Inserción masiva optimizada por lotes
                df.to_sql(
                    name=tabla_oracle, 
                    con=conexion_directa, 
                    if_exists='append', 
                    index=False, 
                    dtype=diccionario_tipos,
                    schema='SYSTEM',
                    chunksize=10000
                )
                
                conexion_directa.commit()
                print(f"✅ Éxito: {len(df)} registros insertados en {tabla_oracle}.")
            else:
                print(f"❌ Archivo no encontrado: {ruta_csv}")

    print("\n--> ¡FASE 3 FINALIZADA! Tu tabla FACT_ACCIDENTE quedó totalmente poblada.")

except Exception as error_global:
    print(f"\n❌ Error durante la inserción masiva: {error_global}")