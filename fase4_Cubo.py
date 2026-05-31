import pandas as pd
import os
import warnings # 1. Configuración del manejo de alertas de Python

from sqlalchemy import create_engine
from sqlalchemy.types import VARCHAR

# Silenciar de forma absoluta cualquier tipo de UserWarning generado por Pandas o SQLAlchemy
warnings.filterwarnings("ignore", category=UserWarning)
warnings.simplefilter(action='ignore', category=UserWarning)

print("============================================================")
print("===== FASE 4: CREACIÓN DEL CUBO LÓGICO Y DATA ANALYSIS =====")
print("============================================================")
 
# 1. Configuración de la cadena de conexión de Oracle
CONEXION_ORACLE = "oracle+oracledb://SYSTEM:Oracle2026*@localhost:1521/?service_name=XE"

try:
    engine = create_engine(CONEXION_ORACLE)
    print("-> Conexión exitosa al Data Warehouse de Oracle usando Thin Driver (oracledb).")
except Exception as e:
    print(f"❌ Error de conexión: {e}")
    exit()

    print("\n--- Fase 4: Creación del Cubo Lógico (Analítica) ---")

    with engine.connect() as conn:
        conn.execute(text("""
            CREATE VIEW V_CUBO_LOGISTICA_TRANSPORTE AS
            SELECT
                f.ID_VIAJE,
                f.PLACA,
                v.MODELO,
                f.KM_RECORRIDOS,
                f.GALONES,
                ROUND(f.KM_RECORRIDOS / f.GALONES, 2) as RENDIMIENTO_KMG,
                CASE
                    WHEN (f.KM_RECORRIDOS / f.GALONES) < 4 THEN 'ALERTA: POSIBLE FUGA O ROBO'
                    WHEN (f.KM_RECORRIDOS / f.GALONES) > 15 THEN 'ALERTA: FALLA SENSOR KM'
                    ELSE 'OPERACIÓN NORMAL'
                END as DIAGNOSTICO_BI
            FROM FACT_VIAJES f
            JOIN DIM_VEHICULOS v ON f.PLACA = v.PLACA
        """))
        conn.commit()
    print("✅ Fase 4 finalizada: Cubo Lógico listo para explotación.")

    # ==========================================
    # RESULTADO FINAL: EXTRACCIÓN DE CONOCIMIENTO
    # ==========================================
    print("\n--- RESULTADO FINAL DEL CUBO LOGÍSTICO ---")
    df_resultado = pd.read_sql("SELECT * FROM V_CUBO_LOGISTICA_TRANSPORTE", engine)
    print(df_resultado.to_string())
