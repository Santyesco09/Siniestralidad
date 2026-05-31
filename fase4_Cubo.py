import pandas as pd
import warnings
from sqlalchemy import create_engine

# Silenciar de forma absoluta cualquier tipo de UserWarning generado por Pandas o SQLAlchemy
warnings.filterwarnings("ignore")

print("============================================================")
print("===== FASE 4: EXTRACCIÓN DE CONOCIMIENTO Y DATAMARTS ======")
print("============================================================")

# 1. Configuración de la cadena de conexión optimizada de Oracle XE
CONEXION_ORACLE = "oracle+oracledb://SYSTEM:Oracle2026*@localhost:1521/?service_name=XEPDB1"

try:
    engine = create_engine(CONEXION_ORACLE)
    print("-> Conexión exitosa al Data Warehouse de Oracle usando Thin Driver (oracledb).")
except Exception as e:
    print(f"❌ Error de conexión: {e}")
    exit()

print("\n📥 Extrayendo registros consolidados desde las vistas del cubo multidimensional...")

# 2. Carga y etiquetado de datos históricos de los dos periodos analíticos
df_2020 = pd.read_sql("SELECT * FROM V_CUBO_ACCIDENTALIDAD_2020", engine)
df_2025 = pd.read_sql("SELECT * FROM V_CUBO_ACCIDENTALIDAD_2025", engine)

df_2020['ANIO_PERIODO'] = 2020
df_2025['ANIO_PERIODO'] = 2025

# 3. Consolidación en el DataFrame Maestro de explotación de negocio
df_cubo = pd.concat([df_2020, df_2025], ignore_index=True)

print("\n✅ Extracción y consolidación completada. Primeras filas del DataFrame resultante:")
print(df_cubo.head())
print(f"✅ DataWarehouse unificado: {len(df_cubo)} filas lógicas listas para estadistica.")


# 1. ESTACIONALIDAD MENSUAL DE ACCIDENTES Y HERIDOS
print("\n" + "="*65)
print("\t1. ESTACIONALIDAD MENSUAL DE ACCIDENTES Y HERIDOS")
print("="*65)

meses = df_cubo.groupby(['ANIO_PERIODO', 'mes'])[['total_accidentes', 'total_heridos']].sum().reset_index()
meses = meses.rename(columns={'mes': 'MES_NUM'})

print(meses)
print("\n[Métricas de Control de Variabilidad]")
print(meses.describe())

# 2. TOP 10 CAUSAS DE ACCIDENTALIDAD MÁS RECURRENTES
print("\n" + "="*65)
print("\t2. TOP 10 CAUSAS DE ACCIDENTALIDAD MÁS RECURRENTES")
print("="*65)

causas = df_cubo.groupby('causa')['total_accidentes'].sum().reset_index()
causas_top = causas.sort_values(by='total_accidentes', ascending=False).head(10)

print(causas_top)
print("\n[Métricas de Control de Variabilidad]")
print(causas.describe())