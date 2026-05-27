import pandas as pd
import os

ruta_archivo = "../Archivos/BD_Siniestralidad.csv"

ruta_absoluta = os.path.join(os.getcwd(), ruta_archivo)

data = pd.read_csv(ruta_absoluta)
df = pd.DataFrame(data)

print(df)