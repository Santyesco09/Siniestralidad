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

# 2. Carga directa de datos desde las vistas relacionales de Oracle
df_2020 = pd.read_sql("SELECT * FROM V_CUBO_ACCIDENTALIDAD_2020", engine)
df_2025 = pd.read_sql("SELECT * FROM V_CUBO_ACCIDENTALIDAD_2025", engine)

# 3. Homogeneización de metadatos (Previene fallos por mayúsculas/minúsculas de Oracle)
df_2020.columns = df_2020.columns.str.lower()
df_2025.columns = df_2025.columns.str.lower()

# 4. Inyección del atributo dimensional de control temporal
df_2020['anio_periodo'] = 2020
df_2025['anio_periodo'] = 2025

# 5. CONSOLIDACIÓN ÚNICA: Data Mart Maestro para Explotación Analítica y Power BI
df_cubo = pd.concat([df_2020, df_2025], axis=0, ignore_index=True)
print(f"✅ DataWarehouse unificado: {len(df_cubo)} registros analíticos listos para auditoría estadística.")

# ==================================================================== #
# REESTRUCTURACIÓN DE COLUMNAS EXIGIDAS PARA EL ARCHIVO PLANO CSV
# ==================================================================== #
# Crear columna indexada 'Siniestro' iniciando desde 1
df_cubo.insert(0, 'Siniestro', range(1, len(df_cubo) + 1))

# Crear columna 'Año' duplicando el valor de control temporal e insertarla en la segunda posición
df_cubo.insert(1, 'Año', df_cubo['anio_periodo'])

# ==================================================================== #
# EXPORTACIÓN DEL DATAMART PARA POWER BI
# ==================================================================== #
print("\n" + "="*65)
print("\tGENERACIÓN DEL DATASET CONSOLIDADO (2020 - 2025)")
print("="*65)

RUTA_OUTPUT_BI = "accidentalidad_2020_2025.csv"

try:
    # index=False evita añadir una columna innecesaria de números de fila al modelo de datos de Power BI
    df_cubo.to_csv(RUTA_OUTPUT_BI, index=False, encoding='utf-8-sig')
    print(f"✅ ¡ÉXITO! Dataset unificado exportado correctamente en: '{RUTA_OUTPUT_BI}'")
    print("   Listo para ser importado de forma directa en Power BI con columnas 'Siniestro' y 'Año'.")
except Exception as e:
    print(f"❌ Error crítico al escribir el archivo CSV: {e}")

# ==================================================================== #
# ANALISIS 1: Distribución Geográfica de Siniestralidad por Localidad
# ==================================================================== #
print("\n" + "="*65)
print("\t1. TOP LOCALIDADES CON MAYOR VOLUMEN DE ACCIDENTALIDAD")
print("="*65)
localidades = df_cubo.groupby(['anio_periodo', 'localidad'])['total_accidentes'].sum().reset_index()
print(localidades.sort_values(by=['anio_periodo', 'total_accidentes'], ascending=[True, False]))
print("\n[Métricas de Control de Variabilidad]")
print(localidades.describe())

# ==================================================================== #
# ANALISIS 2: Estados Críticos de Operación bajo Reglas de BI
# ==================================================================== #
print("\n" + "="*65)
print("\t2. VOLUMEN DE ACCIDENTES POR DIAGNÓSTICO OPERATIVO (BI)")
print("="*65)
diagnostico = df_cubo.groupby(['anio_periodo', 'diagnostico_operativo'])['total_accidentes'].sum().reset_index()
print(diagnostico)
print("\n[Métricas de Control de Variabilidad]")
print(diagnostico.describe())

# ==================================================================== #
# ANALISIS 3: Top 10 Causas de Accidentalidad más Frecuentes
# ==================================================================== #
print("\n" + "="*65)
print("\t3. TOP 10 CAUSAS DE ACCIDENTALIDAD MÁS RECURRENTES")
print("="*65)
causas = df_cubo.groupby('causa')['total_accidentes'].sum().reset_index()
causas_top = causas.sort_values(by='total_accidentes', ascending=False).head(10)
print(causas_top)
print("\n[Métricas de Control de Variabilidad]")
print(causas.describe())

# ==================================================================== #
# ANALISIS 4: Análisis de Siniestralidad por Franja Horaria (MODIFICADO)
# ==================================================================== #
print("\n" + "="*65)
print("\t4. DISTRIBUCIÓN DE SINIESTRALIDAD POR FRANJA HORARIA (HORA DEL DÍA)")
print("="*65)
# Se modificó la agrupación de 'dia' a 'hora' para evaluar la evolución temporal diaria
horas_siniestros = df_cubo.groupby(['anio_periodo', 'hora'])['total_accidentes'].sum().reset_index()
print(horas_siniestros.sort_values(by=['anio_periodo', 'total_accidentes'], ascending=[True, False]))
print("\n[Métricas de Control de Variabilidad]")
print(horas_siniestros.describe())

# ==================================================================== #
# ANALISIS 5: Tipología de Vehículos con Mayor Índice de Siniestralidad
# ==================================================================== #
print("\n" + "="*65)
print("\t5. CANTIDAD DE SINIESTROS SEGÚN LA CLASE DE VEHÍCULO")
print("="*65)
vehiculos = df_cubo.groupby(['anio_periodo', 'vehiculo_clase'])['total_accidentes'].sum().reset_index()
print(vehiculos.sort_values(by=['anio_periodo', 'total_accidentes'], ascending=[True, False]))
print("\n[Métricas de Control de Variabilidad]")
print(vehiculos.describe())

# ==================================================================== #
# ANALISIS 6: Índice de Fatalidad según la Condición del Actor Vial
# ==================================================================== #
print("\n" + "="*65)
print("\t6. TOTAL FATALIDADES SEGÚN LA CONDICION DEL ACTOR VIAL")
print("="*65)
fatalidades = df_cubo.groupby(['anio_periodo', 'actor_condicion'])['total_fatalidades'].sum().reset_index()
print(fatalidades.sort_values(by=['anio_periodo', 'total_fatalidades'], ascending=[True, False]))
print("\n[Métricas de Control de Variabilidad]")
print(fatalidades.describe())

# ==================================================================== #
# ANALISIS 7: Estacionalidad Mensual de Siniestros y Volumen de Lesionados
# ==================================================================== #
print("\n" + "="*65)
print("\t7. ESTACIONALIDAD MENSUAL DE ACCIDENTES Y HERIDOS")
print("="*65)
meses = df_cubo.groupby(['anio_periodo', 'mes'])[['total_accidentes', 'total_heridos']].sum().reset_index()
print(meses.sort_values(by=['anio_periodo', 'mes']))
print("\n[Métricas de Control de Variabilidad]")
print(meses.describe())

# ==================================================================== #
# ANALISIS 8: Impacto del Estado y Condiciones de la Vía en el Riesgo
# ==================================================================== #
print("\n" + "="*65)
print("\t8. SINIESTROS ASOCIADOS AL ESTADO Y CONDICIÓN DE LA VÍA")
print("="*65)
vias = df_cubo.groupby(['via_estado', 'via_condiciones'])[['total_accidentes', 'total_fatalidades']].sum().reset_index()
print(vias.sort_values(by='total_accidentes', ascending=False))
print("\n[Métricas de Control de Variabilidad]")
print(vias.describe())

# ==================================================================== #
# ANALISIS 9: Comportamiento Demográfico: Edad Promedio y Género
# ==================================================================== #
print("\n" + "="*65)
print("\t9. EDAD PROMEDIO DE LOS AFECTADOS SEGÚN GÉNERO")
print("="*65)
demografia = df_cubo.groupby(['anio_periodo', 'actor_sexo'])['edad_promedio'].mean().reset_index()
print(demografia)
print("\n[Métricas de Control de Variabilidad]")
print(demografia.describe())

# ==================================================================== #
# ANALISIS 10: Auditoría Micro-Geográfica: Barrios Críticos
# ==================================================================== #
print("\n" + "="*65)
print("\t10. TOP 15 BARRIOS CON MAYOR CONCENTRACIÓN DE LESIONADOS (HERIDOS)")
print("="*65)
barrios = df_cubo.groupby(['localidad', 'barrio'])['total_heridos'].sum().reset_index()
print(barrios.sort_values(by='total_heridos', ascending=False).head(15))
print("\n[Métricas de Control de Variabilidad]")
print(barrios.describe())

print("\n--> ¡Análisis estadísticos consolidados finalizados para soporte del proyecto!")