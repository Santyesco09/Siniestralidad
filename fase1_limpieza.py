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
CARPETA_ORIGEN = "CSV"
CARPETA_DESTINO = "datos_limpios"

# Crear el directorio de salida si no existe en el espacio de trabajo
if not os.path.exists(CARPETA_DESTINO):
    os.makedirs(CARPETA_DESTINO)

print("Cargando y normalizando las llaves de texto originales...")

# 1. Función ETL para homologar cadenas de texto y remover impurezas de codificación
def cargar_limpio(nombre_archivo):
    path = os.path.join(CARPETA_ORIGEN, nombre_archivo)
    # low_memory=False optimiza la lectura de archivos grandes; dtype=str evita casteos erróneos automáticos
    df = pd.read_csv(path, low_memory=False, dtype=str)
    
    # NORMALIZACIÓN CRÍTICA: Eliminar comillas simples, espacios en blanco y forzar mayúsculas
    # Esto asegura que 'A123' y ' A123 ' se reconozcan como la misma entidad relacional
    df['FORMULARIO'] = df['FORMULARIO'].astype(str).str.replace("'", "", regex=False).str.strip().str.upper()
    return df

# Carga masiva de los datasets originales del portal de la Secretaría de Movilidad
df_acc_raw = cargar_limpio('ACCIDENTE.csv')
df_act_raw = cargar_limpio('VM_ACC_ACTOR_VIAL.csv')
df_cau_raw = cargar_limpio('VM_ACC_CAUSA.csv')
df_veh_raw = cargar_limpio('VM_ACC_VEHICULO.csv')
df_via_raw = cargar_limpio('VM_ACC_VIA.csv')

# ==========================================
# CÓDIGO TEMPORAL PARA CAPTURA DEL ANTES
# print("\n--- EVIDENCIA ANTES: ESTRUCTURA CRUDA DEL DATAFRAME ---")
# print(df_acc_raw.info())
# print(df_acc_raw[['LATITUD', 'LONGITUD', 'ANO_OCURRENCIA_ACC']].head(10))
# print("------------------------------------------------------\n")
# ==========================================

# 2. FILTRADO TEMPORAL: Acotar el universo de hechos al alcance del proyecto (2020 y 2025)
# Se eliminan puntos flotantes residuales del string (ej: '2020.0' -> '2020')
df_acc_raw['ANO_OCURRENCIA_ACC'] = df_acc_raw['ANO_OCURRENCIA_ACC'].astype(str).str.replace('.', '', regex=False).str.strip()
df_acc_raw['ANO_OCURRENCIA_ACC'] = pd.to_numeric(df_acc_raw['ANO_OCURRENCIA_ACC'], errors='coerce')

# Segmentación por teoría de conjuntos usando .isin()
df_fact = df_acc_raw[df_acc_raw['ANO_OCURRENCIA_ACC'].isin([2020, 2025])].copy()

# Data Quality: Remover registros nulos o cadenas vacías en la llave primaria de Hechos
df_fact = df_fact[df_fact['FORMULARIO'].notna() & (df_fact['FORMULARIO'] != 'NAN') & (df_fact['FORMULARIO'] != '')]

# Limpieza de columnas de control temporal que ya no se requieren en el Data Warehouse
df_fact.drop(columns=['ANO_OCURRENCIA_ACC'], inplace=True, errors='ignore')

print(f"-> Tabla de hechos filtrada: {len(df_fact)} accidentes detectados.")

# 3. EXTRACCIÓN SELECCIÓND DE ATRIBUTOS (Mapeo al Modelo de Datos Fisico / DDL)
df_act = df_act_raw[['FORMULARIO', 'CONDICION', 'ESTADO', 'MUERTE_POSTERIOR', 'EDAD', 'GENERO']].copy()
df_cau = df_cau_raw[['FORMULARIO', 'CODIGO_CAUSA', 'NOMBRE']].copy() 
df_veh = df_veh_raw[['FORMULARIO', 'PLACA', 'CLASE', 'SERVICIO']].copy() 
df_via = df_via_raw[['FORMULARIO', 'CODIGO_VIA', 'SUPERFICIE_RODADURA', 'ESTADO', 'CONDICIONES', 'AGENTE']].copy()

# Renombrar atributos específicos para emparejar con las especificaciones del Data Warehouse
df_via.rename(columns={'SUPERFICIE_RODADURA': 'SUPERFICIE'}, inplace=True)
df_veh.rename(columns={'PLACA': 'PLACA_ID'}, inplace=True)

# 4. DESNORMALIZACIÓN Y CONTROL DE GRANULARIDAD
# Garantiza que el grano de las dimensiones sea único por número de Formulario (Relación 1 a Muchos)
df_act.drop_duplicates(subset=['FORMULARIO'], keep='first', inplace=True)
df_cau.drop_duplicates(subset=['FORMULARIO'], keep='first', inplace=True)
df_veh.drop_duplicates(subset=['FORMULARIO'], keep='first', inplace=True)
df_via.drop_duplicates(subset=['FORMULARIO'], keep='first', inplace=True)

# 5. ESTRATEGIA DE MITIGACIÓN DE DATOS HUÉRFANOS (Late-Arriving Dimensions / Early Facts)
# Creamos un set indexado con los formularios reales de la tabla de hechos
formularios_en_hechos = set(df_fact['FORMULARIO'])

def asegurar_integridad_dimension(df_dim, nombre_id_dim, columnas_descriptivas):
    formularios_en_dim = set(df_dim['FORMULARIO'])
    
    # OPERACIÓN DE CONJUNTOS: Detectar llaves en hechos que no existen en la dimensión descargada
    huorfanos = formularios_en_hechos - formularios_en_dim
    
    if len(huorfanos) > 0:
        # Generar un DataFrame sintético con las llaves faltantes
        df_contingencia = pd.DataFrame({'FORMULARIO': list(huorfanos)})
        # Asignar la bandera por defecto para el negocio y Power BI
        for col in columnas_descriptivas:
            df_contingencia[col] = "NO REGISTRA EN ORIGEN"
            
        # Concatenación vertical: Unir registros reales con los registros de contingencia fabricados
        df_dim = pd.concat([df_dim, df_contingencia], ignore_index=True)
    
    # Renombrar formalmente el campo llave de la dimensión según el modelo estrella
    df_dim.rename(columns={'FORMULARIO': nombre_id_dim}, inplace=True)
    df_dim.fillna("NO REGISTRA", inplace=True)
    return df_dim

print("Modelando y resolviendo integridad referencial de dimensiones...")
df_act = asegurar_integridad_dimension(df_act, 'ID_ACCIDENTADO', ['CONDICION', 'ESTADO', 'MUERTE_POSTERIOR', 'EDAD', 'GENERO'])
df_cau = asegurar_integridad_dimension(df_cau, 'ID_CAUSA', ['CODIGO_CAUSA', 'NOMBRE'])
df_veh = asegurar_integridad_dimension(df_veh, 'ID_PLACA', ['PLACA_ID', 'CLASE', 'SERVICIO'])
df_via = asegurar_integridad_dimension(df_via, 'ID_VIA', ['CODIGO_VIA', 'SUPERFICIE', 'ESTADO', 'CONDICIONES', 'AGENTE'])

# 6. ASIGNACIÓN DE LLAVES FORÁNEAS (Foreign Keys) EN LA TABLA DE HECHOS
# Como usamos llaves naturales alfanuméricas idénticas, el formulario mapea directamente a cada dimensión
df_fact['ID_ACCIDENTADO'] = df_fact['FORMULARIO']
df_fact['ID_CAUSA'] = df_fact['FORMULARIO']
df_fact['ID_PLACA'] = df_fact['FORMULARIO']
df_fact['ID_VIA'] = df_fact['FORMULARIO']

# Estructurar el orden secuencial definitivo de las columnas para persistencia física
df_fact = df_fact[[
    'FORMULARIO', 'ID_ACCIDENTADO', 'ID_CAUSA', 'ID_PLACA', 'ID_VIA',
    'FECHA_HORA_ACC', 'DIA_OCURRENCIA_ACC', 'DIRECCION', 'GRAVEDAD', 
    'CLASE_ACC', 'LOCALIDAD', 'LATITUD', 'LONGITUD', 'BARRIO'
]]

df_act = df_act[['ID_ACCIDENTADO', 'CONDICION', 'ESTADO', 'MUERTE_POSTERIOR', 'EDAD', 'GENERO']]
df_cau = df_cau[['ID_CAUSA', 'CODIGO_CAUSA', 'NOMBRE']]
df_veh = df_veh[['ID_PLACA', 'PLACA_ID', 'CLASE', 'SERVICIO']]
df_via = df_via[['ID_VIA', 'CODIGO_VIA', 'SUPERFICIE', 'ESTADO', 'CONDICIONES', 'AGENTE']]

# 7. PERSISTENCIA EN ALMACENAMIENTO LOCAL (Escritura de los entregables CSV limpios)
df_fact.to_csv(os.path.join(CARPETA_DESTINO, 'fact_accidente.csv'), index=False)
df_act.to_csv(os.path.join(CARPETA_DESTINO, 'dim_actor.csv'), index=False)
df_cau.to_csv(os.path.join(CARPETA_DESTINO, 'dim_causa.csv'), index=False)
df_veh.to_csv(os.path.join(CARPETA_DESTINO, 'dim_vehiculo.csv'), index=False)
df_via.to_csv(os.path.join(CARPETA_DESTINO, 'dim_via.csv'), index=False)

print(f"\n--> ¡FASE 1 COMPLETADA CON LLAVES NATURALES ORIGINALES!")
print(f"Registros en Fact Hechos: {len(df_fact)}")
print(f"Registros en Dim_Actor  : {len(df_act)} ")
print(f"Registros en Dim_Causa  : {len(df_cau)} ")
print(f"Registros en Dim_Vehiculo: {len(df_veh)} ")
print(f"Registros en Dim_Via    : {len(df_via)} ")
print(f"Todo listo en '{CARPETA_DESTINO}/' para subirlo a la base de datos Oracle.")