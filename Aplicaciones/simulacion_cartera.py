import pandas as pd
from datetime import datetime
from dateutil.relativedelta import relativedelta

# Parámetros
inicio = datetime(2025, 7, 1)

meses = int(input("Indique cuantos años:"))
meses = meses * 12
inversion_inicial = int(input("Indique la aportación inicial:"))
aporte_mensual = int(input("Indique el aporte mensual:"))
tae = int(input("Indique el rendimiento %:"))
rentabilidad_mensual = (1 + (tae/100)) ** (1/12) - 1  # 6% anual

# Cálculo
datos = []
capital = 0

for i in range(meses):
    fecha = inicio + relativedelta(months=i)
    aporte = inversion_inicial if i == 0 else aporte_mensual
    capital = capital * (1 + rentabilidad_mensual) + aporte
    datos.append((fecha.strftime("%Y-%m-%d"), aporte, round(capital, 2)))

# Exportar a Excel
df = pd.DataFrame(datos, columns=["Fecha", "Aportación", "Capital estimado"])
df.to_excel("simulacion_ing.xlsx", index=False)
