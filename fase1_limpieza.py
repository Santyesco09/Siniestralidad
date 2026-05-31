import pandas as pd
import numpy as np
import os
import warnings

# Desactivar advertencias de rendimiento o asignación por copia de Pandas
warnings.filterwarnings('ignore')

print("=======================================================")
print("======== FASE 1: LIMPIEZA CON LLAVES NATURALES ========")
print("=======================================================")

# Definición de rutas del entorno local de datos
CARPETA_ORIGEN  = "csv"
CARPETA_DESTINO = "datos_limpios"

# Crear el directorio de salida si no existe en el espacio de trabajo
if not os.path.exists(CARPETA_DESTINO):
    os.makedirs(CARPETA_DESTINO)

print("Cargando y normalizando las llaves de texto originales...")

# 1. Función ETL para homologar cadenas de texto y remover impurezas de codificación
def cargar_limpio(nombre_archivo):
    path = os.path.join(CARPETA_ORIGEN, nombre_archivo)
    if not os.path.exists(path):
        print(f"❌ Error: El archivo {nombre_archivo} no existe en la carpeta {CARPETA_ORIGEN}")
        return pd.DataFrame(columns=['FORMULARIO'])
    
    df = pd.read_csv(path, low_memory=False, dtype=str)

    # NORMALIZACIÓN CRÍTICA: Eliminar comillas simples, espacios en blanco y forzar mayúsculas
    if 'FORMULARIO' in df.columns:
        df['FORMULARIO'] = df['FORMULARIO'].astype(str).str.replace("'", "", regex=False).str.strip().str.upper()
    return df

# Carga masiva de los datasets originales
df_acc_raw = cargar_limpio('ACCIDENTE.csv')
df_act_raw = cargar_limpio('VM_ACC_ACTOR_VIAL.csv')
df_cau_raw = cargar_limpio('VM_ACC_CAUSA.csv')
df_via_raw = cargar_limpio('VM_ACC_VIA.csv')

# 2. FILTRADO TEMPORAL: Acotar el universo de hechos al alcance del proyecto (2020 y 2025)
df_acc_raw['ANO_OCURRENCIA_ACC'] = df_acc_raw['ANO_OCURRENCIA_ACC'].astype(str).str.replace('.', '', regex=False).str.strip()
df_acc_raw['ANO_OCURRENCIA_ACC'] = pd.to_numeric(df_acc_raw['ANO_OCURRENCIA_ACC'], errors='coerce')

# Segmentación por teoría de conjuntos usando .isin()
df_fact = df_acc_raw[df_acc_raw['ANO_OCURRENCIA_ACC'].isin([2020, 2025])].copy()

# Data Quality: Remover registros nulos o cadenas vacías en la llave primaria de Hechos
df_fact = df_fact[df_fact['FORMULARIO'].notna() & (df_fact['FORMULARIO'] != 'NAN') & (df_fact['FORMULARIO'] != '')]

# Normalizar CODIGO_ACCIDENTE para usarlo como llave de join con DIM_VIA
if 'CODIGO_ACCIDENTE' in df_fact.columns:
    df_fact['CODIGO_ACCIDENTE'] = df_fact['CODIGO_ACCIDENTE'].astype(str).str.strip()

# Limpieza de columnas de control temporal que ya no se requieren en el Data Warehouse
df_fact.drop(columns=['ANO_OCURRENCIA_ACC'], inplace=True, errors='ignore')

print(f"-> Tabla de hechos filtrada: {len(df_fact)} accidentes detectados.")

# ===========================================================================
# 3. EXTRACCIÓN Y SELECCIÓN DE ATRIBUTOS
# ===========================================================================
formularios_en_hechos = set(df_fact['FORMULARIO'])
codigos_acc_en_hechos = set(df_fact['CODIGO_ACCIDENTE']) if 'CODIGO_ACCIDENTE' in df_fact.columns else set()

# --- DIM_ACTOR: FORMULARIO directo ---
df_act = df_act_raw[df_act_raw['FORMULARIO'].isin(formularios_en_hechos)][
    ['FORMULARIO', 'CONDICION', 'ESTADO', 'MUERTE_POSTERIOR', 'EDAD', 'GENERO']
].copy()

# --- DIM_CAUSA: FORMULARIO directo ---
df_cau = df_cau_raw[df_cau_raw['FORMULARIO'].isin(formularios_en_hechos)][
    ['FORMULARIO', 'CODIGO_CAUSA', 'NOMBRE']
].copy()

# --- DIM_VEHICULO: construida desde ACCIDENTE.csv por FORMULARIO ---
df_veh = df_fact[['FORMULARIO', 'CLASE_ACC']].copy()
df_veh.rename(columns={'CLASE_ACC': 'CLASE'}, inplace=True)
df_veh['PLACA_ID'] = 'SIN REGISTRO'
df_veh['SERVICIO'] = 'SIN REGISTRO'

# --- DIM_VIA: join por CODIGO_ACCIDENTE ---
if 'CODIGO_ACCIDENTE' in df_via_raw.columns:
    df_via_raw['CODIGO_ACCIDENTE'] = df_via_raw['CODIGO_ACCIDENTE'].astype(str).str.strip()
    df_via_filtrada = df_via_raw[df_via_raw['CODIGO_ACCIDENTE'].isin(codigos_acc_en_hechos)][
        ['CODIGO_ACCIDENTE', 'CODIGO_VIA', 'SUPERFICIE_RODADURA', 'ESTADO', 'CONDICIONES', 'AGENTE']
    ].copy()
    df_via_filtrada.rename(columns={'SUPERFICIE_RODADURA': 'SUPERFICIE'}, inplace=True)
    df_via_filtrada.drop_duplicates(subset=['CODIGO_ACCIDENTE'], keep='first', inplace=True)

    # Incorporar el FORMULARIO de la Fact al resultado de VIA (via CODIGO_ACCIDENTE)
    df_via = df_fact[['FORMULARIO', 'CODIGO_ACCIDENTE']].merge(
        df_via_filtrada, on='CODIGO_ACCIDENTE', how='left'
    )[['FORMULARIO', 'CODIGO_VIA', 'SUPERFICIE', 'ESTADO', 'CONDICIONES', 'AGENTE']].copy()
else:
    df_via = pd.DataFrame(columns=['FORMULARIO', 'CODIGO_VIA', 'SUPERFICIE', 'ESTADO', 'CONDICIONES', 'AGENTE'])

# 4. DESNORMALIZACIÓN Y CONTROL DE GRANULARIDAD
df_act.drop_duplicates(subset=['FORMULARIO'], keep='first', inplace=True)
df_cau.drop_duplicates(subset=['FORMULARIO'], keep='first', inplace=True)
df_veh.drop_duplicates(subset=['FORMULARIO'], keep='first', inplace=True)
df_via.drop_duplicates(subset=['FORMULARIO'], keep='first', inplace=True)

# ===========================================================================
# 4.5. CONTROL DE DATA QUALITY EXCLUSIVO PARA EDAD Y FECHAS SEPARADAS
# ===========================================================================
# --- TRATAMIENTO DE EDAD NUMÉRICA ---
edad_numerica = pd.to_numeric(df_act['EDAD'], errors='coerce')
df_act['EDAD'] = edad_numerica.apply(lambda x: int(x) if pd.notna(x) and (0 <= x <= 98) else None)
df_act['EDAD'] = df_act['EDAD'].astype('Int64')

# --- TRATAMIENTO SEPARADO DE FECHA Y HORA ---
if 'FECHA_HORA_ACC' in df_fact.columns:
    df_fact['FECHA_HORA_ACC'] = df_fact['FECHA_HORA_ACC'].astype(str).str.replace('+00', '', regex=False).str.strip()
    df_fact['FECHA_HORA_ACC'] = pd.to_datetime(df_fact['FECHA_HORA_ACC'], errors='coerce', yearfirst=True)
    df_fact['FECHA_HORA_ACC'].fillna(pd.Timestamp('1900-01-01 00:00:00'), inplace=True)
    df_fact['FECHA_ACC'] = df_fact['FECHA_HORA_ACC'].dt.strftime('%Y-%m-%d')
    df_fact['HORA_ACC']  = df_fact['FECHA_HORA_ACC'].dt.strftime('%H:%M:%S')
    df_fact.drop(columns=['FECHA_HORA_ACC'], inplace=True, errors='ignore')
else:
    # Contingencia en caso de que ya vengan separadas o la columna se llame FECHA_ACC
    if 'FECHA_ACC' in df_fact.columns:
        df_fact['FECHA_ACC'] = pd.to_datetime(df_fact['FECHA_ACC'], errors='coerce').dt.strftime('%Y-%m-%d')
    else:
        df_fact['FECHA_ACC'] = '1900-01-01'
    if 'HORA_ACC' not in df_fact.columns:
        df_fact['HORA_ACC'] = '00:00:00'

print("Modelando y resolviendo integridad referencial de dimensiones...")

# ===========================================================================
# 5. ESTRATEGIA DE MITIGACIÓN DE DATOS HUÉRFANOS (Modificada y Corregida)
# ===========================================================================
def asegurar_integridad_dimension(df_dim, nombre_id_dim, columnas_descriptivas):
    formularios_en_dim = set(df_dim['FORMULARIO'])
    huorfanos = formularios_en_hechos - formularios_en_dim

    if len(huorfanos) > 0:
        df_contingencia = pd.DataFrame({'FORMULARIO': list(huorfanos)})
        for col in columnas_descriptivas:
            if col == 'EDAD':
                df_contingencia[col] = None
            else:
                df_contingencia[col] = "SIN REGISTRO"
        df_dim = pd.concat([df_dim, df_contingencia], ignore_index=True)

    df_dim.rename(columns={'FORMULARIO': nombre_id_dim}, inplace=True)

    for col in df_dim.columns:
        if col == 'EDAD':
            df_dim[col] = df_dim[col].astype('Int64')
        elif col != nombre_id_dim:
            df_dim[col] = df_dim[col].fillna("SIN REGISTRO")

    return df_dim

# REASIGNACIÓN CORRECTA CAPTURANDO EL VALOR DE RETORNO
df_act = asegurar_integridad_dimension(df_act, 'ID_ACCIDENTADO', ['CONDICION', 'ESTADO', 'MUERTE_POSTERIOR', 'EDAD', 'GENERO'])
df_cau = asegurar_integridad_dimension(df_cau, 'ID_CAUSA',        ['CODIGO_CAUSA', 'NOMBRE'])
df_veh = asegurar_integridad_dimension(df_veh, 'ID_PLACA',        ['PLACA_ID', 'CLASE', 'SERVICIO'])
df_via = asegurar_integridad_dimension(df_via, 'ID_VIA',          ['CODIGO_VIA', 'SUPERFICIE', 'ESTADO', 'CONDICIONES', 'AGENTE'])

# 6. ASIGNACIÓN DE LLAVES FORÁNEAS (Foreign Keys) EN LA TABLA DE HECHOS
df_fact['ID_ACCIDENTADO'] = df_fact['FORMULARIO']
df_fact['ID_CAUSA']       = df_fact['FORMULARIO']
df_fact['ID_PLACA']       = df_fact['FORMULARIO']
df_fact['ID_VIA']         = df_fact['FORMULARIO']

# Rellenar coordenadas vacías por seguridad estructural
df_fact['LATITUD']  = df_fact['LATITUD'].fillna('0.0')
df_fact['LONGITUD'] = df_fact['LONGITUD'].fillna('0.0')

# Estructurar el orden secuencial definitivo exigido por Oracle DDL
df_fact = df_fact[[
    'FORMULARIO', 'ID_ACCIDENTADO', 'ID_CAUSA', 'ID_PLACA', 'ID_VIA',
    'FECHA_ACC', 'HORA_ACC', 'DIA_OCURRENCIA_ACC', 'DIRECCION', 'GRAVEDAD',
    'CLASE_ACC', 'LOCALIDAD', 'LATITUD', 'LONGITUD', 'BARRIO'
]]

df_act = df_act[['ID_ACCIDENTADO', 'CONDICION', 'ESTADO', 'MUERTE_POSTERIOR', 'EDAD', 'GENERO']]
df_cau = df_cau[['ID_CAUSA', 'CODIGO_CAUSA', 'NOMBRE']]
df_veh = df_veh[['ID_PLACA', 'PLACA_ID', 'CLASE', 'SERVICIO']]
df_via = df_via[['ID_VIA', 'CODIGO_VIA', 'SUPERFICIE', 'ESTADO', 'CONDICIONES', 'AGENTE']]

# ===========================================================================
# 6.5. VALIDADOR DE INTEGRIDAD REFERENCIAL
# ===========================================================================
print("\n[AUDITORÍA] Verificando cobertura referencial antes de persistir...")

def validar_integridad(df_fact_local, df_dim, fk_col, pk_col, nombre_dim):
    fks     = set(df_fact_local[fk_col].astype(str).str.strip())
    pks     = set(df_dim[pk_col].astype(str).str.strip())
    matches = len(fks & pks)
    huerfanos = len(fks - pks)
    cobertura = round((matches / len(fks)) * 100, 2) if len(fks) > 0 else 0
    print(f"  [{nombre_dim}] Cobertura: {cobertura}% | Matches: {matches} | Huérfanos reales: {huerfanos}")

validar_integridad(df_fact, df_act, 'ID_ACCIDENTADO', 'ID_ACCIDENTADO', 'DIM_ACTOR_VIAL')
validar_integridad(df_fact, df_cau, 'ID_CAUSA',       'ID_CAUSA',       'DIM_CAUSA')
validar_integridad(df_fact, df_veh, 'ID_PLACA',       'ID_PLACA',       'DIM_VEHICULO')
validar_integridad(df_fact, df_via, 'ID_VIA',         'ID_VIA',         'DIM_VIA')

# 7. PERSISTENCIA EN ALMACENAMIENTO LOCAL
try:
    df_fact.to_csv(os.path.join(CARPETA_DESTINO, 'fact_accidente.csv'), index=False, encoding='utf-8')
    df_act.to_csv(os.path.join(CARPETA_DESTINO, 'dim_actor.csv'),      index=False, encoding='utf-8')
    df_cau.to_csv(os.path.join(CARPETA_DESTINO, 'dim_causa.csv'),      index=False, encoding='utf-8')
    df_veh.to_csv(os.path.join(CARPETA_DESTINO, 'dim_vehiculo.csv'),   index=False, encoding='utf-8')
    df_via.to_csv(os.path.join(CARPETA_DESTINO, 'dim_via.csv'),        index=False, encoding='utf-8')
    
    print("\n--> ¡FASE 1 COMPLETADA CON INTEGRIDAD REFERENCIAL ABSOLUTA!")
    print(f"Registros en Fact Hechos : {len(df_fact)}")
    print(f"Registros en Dim_Actor   : {len(df_act)}")
    print(f"Registros en Dim_Causa   : {len(df_cau)}")
    print(f"Registros en Dim_Vehiculo: {len(df_veh)}")
    print(f"Registros en Dim_Via     : {len(df_via)}")
except Exception as e:
    print(f"❌ Error al guardar archivos planos: {e}")