from sqlalchemy import create_engine, text #type:ignore
import pandas as pd
from datetime import datetime

date = datetime.now().strftime("%Y%m%d%H%M%S")
ddbb_name = "Coronita"
referencia = "3810"

fecha_inicio = '2025-12-01'
fecha_fin = '2026-03-10'

def hora():
    hora = datetime.now().strftime("%H:%M:%S")
    return hora

print(f"Hora de inicio: {hora()}")

# --- CONEXIÓN SQLALCHEMY ---

engine = create_engine("mssql+pyodbc://@XGA_PROD")

# --- QUERY SQL (rango de fechas) ---



query2 = text(f"""
              
              
SELECT
    CodigoProdClte AS Referencia,
    SSCCPalet,
    ID_Doc
    
FROM
    vExtraccionesCambioUbicacionAlbaran
WHERE
    ID_Cliente = 944
    AND ID_Almacen = 129
    AND ID_Deposito = 258
    AND TipoMvtoPalet IN ('S', 'E')
    AND CantidadMvtoPalet <> 0
    AND LTRIM(RTRIM(CodigoProdClte)) = {referencia}
    AND ID_Extraccion IS NOT NULL
    AND LTRIM(RTRIM(ID_Extraccion)) <> ''
             """)

 
# --- EJECUTAR CONSULTA ---
with engine.connect() as conn:
    df = pd.read_sql(query2, conn, params={"inicio": fecha_inicio, "fin": fecha_fin} )

# --Metemos en una lista los Albaranes
list_ids = df["ID_Doc"].tolist()

placeholders = ", ".join([f":id{i}" for i in range(len(list_ids))])

query_albaranes = text(f"""
        SELECT
            ID_Doc, FechaDoc, AlbaranDoc
        FROM
            vDocumentos
        WHERE
            ID_Cliente = 944
            AND ID_Almacen = 129
            
            
            AND ID_Doc IN ({placeholders})
    """)

# --- EJECUTAR CONSULTA ALBARANES ---
with engine.connect() as conn:
    df_albaranes = pd.read_sql(query_albaranes, conn, params={"inicio": fecha_inicio, "fin": fecha_fin, **{f"id{i}": id for i, id in enumerate(list_ids)}})

# --- UNIR DATAFRAMES ---
df = df.merge(
    df_albaranes[['ID_Doc','AlbaranDoc', 'FechaDoc']],
    on="ID_Doc",
    how="left"
)

# -- Limpieza
df.drop(columns=['ID_Doc'], inplace=True)

# --- EXPORTAR ---
nombre_archivo = f"{ddbb_name}_{date}.xlsx"
df.to_excel(nombre_archivo, index=False)

print(f"✅ Archivo generado correctamente: {nombre_archivo}")

print(f"Hora de fin: {hora()}")
engine.dispose()



