import pandas as pd
import os

ruta_archivo = "Archivos/BD_Siniestralidad.csv"
ruta_absoluta = os.path.join(os.getcwd(), ruta_archivo)

data = pd.read_csv(ruta_absoluta)
df = pd.DataFrame(data)

# -------------------------------------------------------------------- #
# Localidades con más accidentes
localidad = df['Localidad'].value_counts().reset_index(name='Cantidad')

print("\tLocalidades con más accidentalidad")
print(localidad)
print(localidad.describe())

# -------------------------------------------------------------------- #
# Accidentes más comunes
accidente = df['Clase_Acc'].value_counts().reset_index(name='Cantidad')

print("\n\tCantidad de accidentes")
print(accidente)
print(accidente.describe())

# -------------------------------------------------------------------- #
# Cantidad de siniestros según el tipo de gravedad
gravedad = df['Gravedad_Indicador_Tradicional'].value_counts().reset_index(name='Cantidad')

print("\n\tCantidad de siniestros según el tipo de gravedad")
print(gravedad)
print(gravedad.describe())

# -------------------------------------------------------------------- #
# Horarios con más accidentalidad
agrupado = df.groupby(['Hora_Acc', 'Dia_Semana_Acc']).size().reset_index(name='Cantidad')

# Encontrar el índice del máximo conteo para cada localidad
idxmax_df = agrupado.groupby('Hora_Acc')['Cantidad'].idxmax()

# Obtener los resultados
horario_dia = agrupado.loc[idxmax_df]

print("\n\tHorarios con más accidentalidad")
print(horario_dia)
print(horario_dia.describe())

agrupado = df.groupby(['Dia_Semana_Acc', 'Hora_Acc']).size().reset_index(name='Cantidad')

# Encontrar el índice del máximo conteo para cada localidad
idxmax_df = agrupado.groupby('Dia_Semana_Acc')['Cantidad'].idxmax()

# Obtener los resultados
dia_horario = agrupado.loc[idxmax_df]

print("\n\tHorarios con más accidentalidad")
print(dia_horario)
print(dia_horario.describe())

# -------------------------------------------------------------------- #
# Días con más accidentalidad
fecha = df['Fecha_Acc'].value_counts().reset_index(name='Cantidad')

print("\n\tDías con más accidentes")
print(fecha.head(10))

print("\n\tDías con menos accidentes")
print(fecha.tail(10))
print(fecha.describe())

# -------------------------------------------------------------------- #
# Hora y Día de la semana con mayor frecuencia de accidentes por Localidad
# Agrupar y contar
agrupado = df.groupby(['Localidad', 'Dia_Semana_Acc', 'Hora_Acc']).size().reset_index(name='Cantidad')

# Encontrar el índice del máximo conteo para cada localidad
idxmax_df = agrupado.groupby('Localidad')['Cantidad'].idxmax()

# Obtener los resultados
localidad_dia_fecha = agrupado.loc[idxmax_df]

# Mostrar los resultados
print("\n\tHora y Día con más siniestros por Localidad")
print(localidad_dia_fecha)
print(localidad_dia_fecha.describe())