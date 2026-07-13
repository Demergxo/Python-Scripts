from sqlalchemy import Null, create_engine, text, bindparam
import pandas as pd
from datetime import datetime

date = datetime.now().strftime("%Y%m%d%H%M%S")
ddbb_name = "cruce_Hisense"

fecha_inicio = '2026-07-03'
fecha_fin = '2026-07-12'


def hora():
    hora = datetime.now().strftime("%H:%M:%S")
    return hora

print(f"Hora de inicio: {hora()}")

# --- CONEXIÓN SQLALCHEMY ---

engine = create_engine("mssql+pyodbc://@XGA_PROD")

# --- QUERY SQL (rango de fechas) ---
query = text(f"""
    SELECT
        NombreTipoDocumento AS [Tipo Documento], RTRIM(ID_Doc) AS ID_Doc, RTRIM(AlbaranDoc) AS Albarán, FechaProcesoDoc AS [Fecha Proceso], FechaProgramadaDoc AS [Fecha Programada]
    FROM
        vDocumentos
    WHERE
        ID_Cliente = 847
        AND CodigoTipoDocumento = 'ALB'
        AND CONVERT(date, FechaProcesoDoc) BETWEEN CONVERT(date, :inicio) AND CONVERT(date, :fin)
""")



# --- EJECUTAR CONSULTA ---
with engine.connect() as conn:
    df = pd.read_sql(query, conn, params={"inicio": fecha_inicio, "fin": fecha_fin})


df["Albarán"] = df["Albarán"].astype(str).str.strip()
df["ID_Doc"] = df["ID_Doc"].astype(str).str.strip()
df["Tipo Documento"] = df["Tipo Documento"].astype(str).str.strip()

ids_alb = (
       df.loc[df["Tipo Documento"].eq("Albaran"), "ID_Doc"]
        .dropna()
        .astype(str)
        .unique()
        .tolist()
    )

query_serial = (
    text("""
        SELECT
            ID_Doc, ID_ProdClte, SeriePalet AS [Num Serie]
        FROM SerialPalet
        WHERE ID_Cliente = 847
        AND ID_Doc IN :ids
        
    """).bindparams(bindparam("ids", expanding=True))
)

with engine.connect() as conn:
    df2 = pd.read_sql(query_serial, conn, params={"ids": ids_alb}) #type: ignore
#print(df)

df2["ID_ProdClte"] = df2["ID_ProdClte"].astype(str).str.strip()
df2["ID_Doc"] = df2["ID_Doc"].astype(str).str.strip()
df2["Num Serie"] = df2["Num Serie"].astype(str).str.strip()

ids_prod = (
    df2["ID_ProdClte"]
    .dropna()
    .astype(str)
    .str.strip()
    .unique()
    .tolist()
)


query_maestro = (
    text("""
        SELECT
            ID_ProdClte, CodigoProdClte AS [Referencia], NombreProdClte AS [Descripción]
        FROM ProductosClientes
        WHERE ID_Cliente = 847
        AND ID_ProdClte IN :ids
        
    """).bindparams(bindparam("ids", expanding=True))
)


with engine.connect() as conn:
    df3 = pd.read_sql(query_maestro, conn, params={"ids": ids_prod}) #type: ignore

df3["ID_ProdClte"] = df3["ID_ProdClte"].astype(str).str.strip()
df3["Referencia"] = df3["Referencia"].astype(str).str.strip()
df3["Descripción"] = df3["Descripción"].astype(str).str.strip()



df = df.merge(
    df2,
    on=["ID_Doc"], how="left")

df = df.merge(
    df3,
    on=["ID_ProdClte"], how="left")

#print(df)
df = df.drop(
    columns=["ID_Doc", "ID_ProdClte", "Tipo Documento"],
    errors="ignore"
)

col_move = "Num Serie"
col_reference = "Descripción"

cols =df.columns.tolist()

cols.remove(col_move)

pos = cols.index(col_reference) + 1
cols.insert(pos, col_move)

df = df[cols]

# --- EXPORTAR ---
nombre_archivo = f"{ddbb_name}_{date}.xlsx"
df.to_excel(nombre_archivo, index=False)

print(f"✅ Archivo generado correctamente: {nombre_archivo}")

print(f"Hora de fin: {hora()}")
engine.dispose()



