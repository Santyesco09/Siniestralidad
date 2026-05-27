import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import pymysql
import os

ruta_archivo = "../Archivos/BD_Siniestralidad.csv"

ruta_absoluta = os.path.join(os.getcwd(), ruta_archivo)

data = pd.read_csv(ruta_absoluta)
df = pd.DataFrame(data)

pivot_table = df.pivot_table(index='Dia_Semana_Acc', columns='Hora_Acc', aggfunc='size', fill_value=0)

# Crear el heatmap
plt.figure(figsize=(12, 6))
sns.heatmap(pivot_table, annot=True, fmt="d", cmap="YlOrRd")
plt.title("Frecuencia de Accidentes por Hora y Día")
plt.xlabel("Hora")
plt.ylabel("Día de la Semana")
plt.show()

accidente_counts = df['Clase_Acc'].value_counts()

print("\n\tAnalisis especifico")
localidad_info = input("\nLocalidad: ")
fecha_inicio = input("Fecha de inicio del análisis: ")
fecha_fin = input("Fecha de fin del análisis: ")
hora_inicio = int(input("Hora de incio del análisis: "))
hora_fin = int(input("Hora de fin del análisis: "))

# Crear el gráfico de barras
plt.figure(figsize=(10, 6))
sns.barplot(x=accidente_counts.index, y=accidente_counts.values)
plt.title(f"Cantidad de accidentes por tipo en {localidad_info} ({fecha_inicio} - {fecha_fin})")
plt.xlabel("Tipo de Accidente")
plt.ylabel("Cantidad")
plt.xticks(rotation=45)  # Rotar las etiquetas del eje x para mejor legibilidad
plt.show()