from sqlalchemy import create_engine, text #type:ignore
import pandas as pd
from datetime import datetime

date = datetime.now().strftime("%Y%m%d%H%M%S")
ddbb_name = "Ubicaciones"
fecha_inicio = '2026-02-12'
fecha_fin = '2026-02-14'

def hora():
    hora = datetime.now().strftime("%H:%M:%S")
    return hora

print(f"Hora de inicio: {hora()}")

# --- CONEXIÓN SQLALCHEMY ---

engine = create_engine("mssql+pyodbc://@XGA_PROD")

# --- QUERY SQL (rango de fechas) ---
query = text(f"""
    SELECT
        *
    FROM
        {ddbb_name}
   
    WHERE 
        
        ID_Almacen = 129
        
""")
# AND CONVERT(date, FechaProcesoDoc) BETWEEN CONVERT(date, :inicio) AND CONVERT(date, :fin)


# --- EJECUTAR CONSULTA ---
with engine.connect() as conn:
    df = pd.read_sql(query, conn, params={"inicio": fecha_inicio, "fin": fecha_fin} )

# --- EXPORTAR ---
nombre_archivo = f"{ddbb_name}_{date}.xlsx"
df.to_excel(nombre_archivo, index=False)

print(f"✅ Archivo generado correctamente: {nombre_archivo}")

print(f"Hora de fin: {hora()}")
engine.dispose()



