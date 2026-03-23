from sqlalchemy import create_engine, text, bindparam #type:ignore
import pandas as pd
from datetime import datetime

date = datetime.now().strftime("%Y%m%d%H%M%S")
#ddbb_name = ""

fecha_inicio = '2026-03-09'
fecha_fin = '2026-03-22'

def hora():
    hora = datetime.now().strftime("%H:%M:%S")
    return hora

print(f"Hora de inicio: {hora()}")

# --- CONEXIÓN SQLALCHEMY ---

engine = create_engine("mssql+pyodbc://@XGA_PROD")

# --- QUERY SQL (rango de fechas) ---
query = text("""
    SELECT
        ID_Doc, AlbaranDoc AS [Pedido MSM], CampoCliente AS [Codigo Doc]
    FROM
        vDocumentos
    WHERE 
        ID_Cliente = 944
        AND CONVERT(date, FechaDoc) BETWEEN CONVERT(date, :inicio) AND CONVERT(date, :fin)
        AND CodigoTipoDocumento IN ('RS', 'ALB') 
        AND ID_Almacen = 129
""")

# --- EJECUTAR CONSULTA ---
with engine.connect() as conn:
    df = pd.read_sql(query, conn, params={"inicio": fecha_inicio, "fin": fecha_fin})

df["Pedido MSM"] = df["Pedido MSM"].astype(str).str.strip()
list_ids = df["Pedido MSM"].tolist()
df["ID_Doc"] = df["ID_Doc"].astype(str).str.strip()
list_doc = df["ID_Doc"].tolist()

    #Query acotada a ID_Doc necesarios
if not list_ids:
    raise ValueError("Lista vacía")
    

dfs =[]

placeholders = ", ".join([f":id{i}" for i in range(len(list_ids))])
placeholders2 = ", ".join([f":id{i}" for i in range(len(list_doc))])

query_pend = text(f"""
    SELECT
        AlbaranDoc AS [Pedido MSM],
        FechaTeoricaCargaDoc AS [Fecha Carga],
        ARCDoc AS [Observaciones]
    FROM 
        Documentos
    WHERE 
        ID_Cliente = 944
        AND ID_Almacen = 129
        AND (ID_TipoDocumento = 1 OR ID_TipoDocumento = 3)
        AND CONVERT(datetime, FechaDoc) BETWEEN CONVERT(date, :inicio) AND CONVERT(date, :fin)
        AND AlbaranDoc IN ({placeholders})
    """)

params_ids = {f"id{i}": v for i, v in enumerate(list_ids)}


params = {
    **params_ids,
    "inicio": fecha_inicio,
    "fin": fecha_fin
}

with engine.connect() as conn:
    df_palets = pd.read_sql(query_pend, conn, params=params)
df_palets["Pedido MSM"] = df_palets["Pedido MSM"].str.strip()


df = df.merge(df_palets, on="Pedido MSM", how="left")
df["ID_Doc"] = df["ID_Doc"].astype(str).str.strip()

query_lineas_in = text("""
    SELECT
        AlbaranDoc AS [Pedido MSM],
        CodigoProdClte AS Referencia,        
        SUM(CantidadLinea) AS Palets
    FROM
        vLineasOrdenCompraAlbaranDoc
    WHERE
        ID_Cliente = 944
        AND AlbaranDoc IN :ids
    GROUP BY
        AlbaranDoc, CodigoProdClte
""").bindparams(
    bindparam("ids", expanding=True))

query_lineas_out = text(f"""
    SELECT
        RTRIM(ID_Doc) AS ID_Doc,
        CodigoProdClte AS Referencia,        
        SUM(CantidadTeorica) AS CantidadTeorica
    FROM
        vDocumentoslineasConsulta
    WHERE
        ID_Cliente = 944
        AND ID_Doc IN ({placeholders2})
    GROUP BY RTRIM(ID_Doc), CodigoProdClte, NombreProdClte                                  
""")


params_docs = {f"id{i}": v for i, v in enumerate(list_doc)}


with engine.connect() as conn:
    df_lineas_in = pd.read_sql(query_lineas_in, conn, params={"ids": list_ids}) #type:ignore
    df_lineas_out = pd.read_sql(query_lineas_out, conn, params=params_docs)
df_lineas_in["Pedido MSM"] = df_lineas_in["Pedido MSM"].str.strip()

df = df.merge(df_lineas_in, on="Pedido MSM", how="left")
df = df.merge(df_lineas_out, left_on="ID_Doc", right_on="ID_Doc", how="left")
df = df.drop(columns=["ID_Doc"])

# --- EXPORTAR ---
nombre_archivo = f"booking_{date}.xlsx"
df.to_excel(nombre_archivo, index=False)

print(f"✅ Archivo generado correctamente: {nombre_archivo}")

print(f"Hora de fin: {hora()}")
engine.dispose()



