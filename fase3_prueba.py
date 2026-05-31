import pandas as pd
import os
import sys
import warnings
import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.types import VARCHAR

# 1. Configuración del manejo de alertas de Python
warnings.filterwarnings("ignore", category=UserWarning)
warnings.simplefilter(action='ignore', category=UserWarning)

# Forzar la consola de Windows a usar UTF-8 para evitar el error UnicodeEncodeError (de los emojis/tildes)
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

print("=======================================================")
print("===== FASE 3: AUTOMATIZACIÓN DE CARGA A ORACLE DB =====")
print("=======================================================")

# ==========================================
# 2. CONFIGURACIÓN DE CONEXIÓN
# ==========================================
USER = "system"
PASS = "Oracle2026*"  
HOST = "localhost"
PORT = "1521"
SERVICE = "XEPDB1"

try:
    # Construcción de la URL de conexión para SQLAlchemy + oracledb
    CADENA_CONEXION = f"oracle+oracledb://{USER}:{PASS}@{HOST}:{PORT}/?service_name={SERVICE}"
    engine = create_engine(CADENA_CONEXION)
    
    # Verificación de conexión real e inmediata tocando la base de datos
    with engine.connect() as conn:
        conn.execute(sqlalchemy.text("SELECT 1 FROM DUAL"))
    print("-> [OK] Conexión REAL y exitosa al Data Warehouse de Oracle.")
    
except Exception as e:
    print(f"❌ Error crítico de conexión inicial: {e}")
    print("Verifica si el servicio de Oracle y la instancia (XE/XEPDB1) están activos.")
    sys.exit(1)

CARPETA_DATOS = "CSV/datos_limpios"

# Mapeo ordenado: Primero se cargan todas las Dimensiones, SIEMPRE los Hechos al final
cargas = [
    ('dim_actor.csv', 'DIM_ACTOR_VIAL'),
    ('dim_causa.csv', 'DIM_CAUSA'),
    ('dim_vehiculo.csv', 'DIM_VEHICULO'),
    ('dim_via.csv', 'DIM_VIA'),
    ('fact_accidente.csv', 'FACT_ACCIDENTE') 
]

# ==========================================
# 3. PROCESO DE INYECCIÓN TRANSACCIONAL
# ==========================================
try:
    # engine.begin() abre una transacción única. Si una tabla falla, se aplica ROLLBACK automático
    # para evitar dejar el Data Warehouse con datos parciales o corruptos.
    with engine.begin() as connection:
        for archivo, tabla_oracle in cargas:
            ruta_csv = os.path.join(CARPETA_DATOS, archivo)
            
            if os.path.exists(ruta_csv):
                print(f"\n📥 Cargando {archivo} en la tabla {tabla_oracle}...")
                
                # Leer el CSV forzando la lectura inicial limpia
                df = pd.read_csv(ruta_csv, low_memory=False)
                
                dicitonario_tipos = {}
                
                # --- TRATAMIENTO DE DATOS EXCLUSIVO PARA LA TABLA DE HECHOS ---
                if tabla_oracle == 'FACT_ACCIDENTE':
                    print("   -> Parseando columna FECHA_HORA_ACC al tipo temporal DATE nativo de Oracle...")
                    # Convertir la columna de texto a objetos DateTime reales de Pandas
                    df['FECHA_HORA_ACC'] = pd.to_datetime(df['FECHA_HORA_ACC'], errors='coerce')
                    
                    # Mapeo seguro de coordenadas a VARCHAR para evitar conflictos de precisión float
                    df['LATITUD'] = df['LATITUD'].astype(str)
                    df['LONGITUD'] = df['LONGITUD'].astype(str)
                    dicitonario_tipos = {'LATITUD': VARCHAR(100), 'LONGITUD': VARCHAR(100)}
                
                # Inserción masiva optimizada de Pandas
                df.to_sql(
                    name=tabla_oracle, 
                    con=connection, 
                    if_exists='append', 
                    index=False, 
                    dtype=dicitonario_tipos
                )
                print(f"✅ Éxito: {len(df)} registros insertados con éxito en {tabla_oracle}.")
            else:
                print(f"❌ Archivo no encontrado obligatorio: {ruta_csv}")
                
    print("\n--> ¡FASE 3 FINALIZADA! Transacción confirmada en Oracle (COMMIT ejecutado automáticamente).")

except Exception as e:
    print(f"\n❌ ERROR CRÍTICO DURANTE LA INSERCIÓN: Proceso abortado.")
    print(f"Detalle del error devuelto por el motor Oracle:\n{e}")