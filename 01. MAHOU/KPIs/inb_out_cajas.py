from sqlalchemy import create_engine, text#type:ignore
import pandas as pd
from datetime import datetime
import time
import os

path = os.getcwd()
DB_FILE = f"{path}\\apoyo.db"

date = datetime.now().strftime("%Y%m%d%H%M%S")
ddbb_name = "KPIS_inb_out_cajas"
fecha_inicio = '2026-03-01'
fecha_fin = '2026-03-08'

def hora():
    hora = datetime.now().strftime("%H:%M:%S")
    return hora

def qry_inb_out(fecha_inicio, fecha_fin):
    path = os.getcwd()
    DB_FILE = f"{path}\\apoyo.db"

    date = datetime.now().strftime("%Y%m%d%H%M%S")
    ddbb_name = "KPIS_inb_out_cajas"

    print(f"Hora de inicio: {hora()}")

    # --- CONEXIÓN SQLALCHEMY ---

    engine = create_engine("mssql+pyodbc://@XGA_PROD")

    # --- QUERY SQL (rango de fechas) ---

    query_docs = text("""
        SELECT
            ID_Doc, FechaProcesoDoc AS 'Fecha', AlbaranDoc AS 'Documento', PesoFiege AS 'Peso', ObsEstado
        FROM
            vDocumentos
        WHERE
            ID_Cliente = 944
            AND ID_Almacen = 129
            AND CodigoTipoDocumento = 'ALB'
            AND CodigoTipoEstado IN ('040', '080', '085', '140', '130', '150')
            AND CONVERT(date, FechaProcesoDoc) BETWEEN CONVERT(date, :inicio) AND CONVERT(date, :fin)

    """)

    

    #  ,PoblacionDireccion AS 'Poblacion', CampoCliente AS 'Tipo'

    # ---Ejecutamos la primera consulta ---
    with engine.connect() as conn:
        df_doc = pd.read_sql(query_docs, conn, params={"inicio": fecha_inicio, "fin": fecha_fin})

        # Normalizamos columnas clave
    df_doc["Documento"] = df_doc["Documento"].str.strip()
    for col in ["Fecha"]:
        if col in df_doc.columns:
            df_doc[col] = pd.to_datetime(df_doc[col], errors='coerce').dt.strftime("%d/%m/%Y").fillna("")
    
    
    list_ids = df_doc["ID_Doc"].tolist()

    #Query acotada a ID_Doc necesarios
    if not list_ids:
        print("⚠️ No se encontraron documentos en ese rango")
        return

    placeholders = ", ".join([f":id{i}" for i in range(len(list_ids))])

    #Query acotada a ID_Doc necesarios

    query_dos = text(f"""
        SELECT
            ID_Doc, ID_ProdClte as Referencia, CantidadLineaDoc, ID_IncidenciaLinea
        FROM
            vLineasDocumentos
        WHERE
            ID_Cliente = 944
            AND ID_Almacen = 129
            AND ID_DivisionCliente = 1866
            AND TipoMovimientoLineaDoc = 'S'
            AND ID_Doc IN ({placeholders})
                     """)


    # --- EJECUTAR  SEGUNDA CONSULTA CONSULTA ---

    with engine.connect() as conn:
        df_palets = pd.read_sql(query_dos, conn, params = {f"id{i}": v for i, v in enumerate(list_ids)})

    #HACEMOS MERGE DE LAS DOS CONSULTAS
    
    df = df_doc.merge(
        df_palets,
        on="ID_Doc",
        how="left"
    )

    df["Referencia"] = pd.to_numeric(df["Referencia"], errors="coerce").fillna(0).astype(int).astype(str)

    # --- CONEXIÓN SQLITE (maestro_msm) ---
    engine_sqlite = create_engine(f"sqlite:///{DB_FILE}")
    df_maestro = pd.read_sql("""
        SELECT
            ID_ProdClte, CodigoProdClte, CajasPaletProdClte, ID_ProdClteSustitutivo
        FROM
        maestro_msm
                             
    """, engine_sqlite)

    #Normalizamos

    for col in ["ID_ProdClte", "ID_ProdClteSustitutivo", "CodigoProdClte"]:
        df_maestro[col] = pd.to_numeric(df_maestro[col], errors="coerce")

    #Resolver producto final (con sustituto si existe)

    df_maestro["ID_Final"] = df_maestro["ID_ProdClte"]

    mask = df_maestro["ID_ProdClteSustitutivo"].notna()
    df_maestro.loc[mask, "ID_Final"] = df_maestro.loc[mask, "ID_ProdClteSustitutivo"]

    for col in ["ID_ProdClte", "ID_Final"]:
        df_maestro[col] = df_maestro[col].fillna(0).astype(int).astype(str)

    # Creamos dataframe auxiliar para buscar datos del producto final
    df_lookup = df_maestro[[
        "ID_ProdClte",
        "CodigoProdClte",
        "CajasPaletProdClte"
    ]].rename(columns={
        "ID_ProdClte": "ID_Final",
        "CodigoProdClte": "Codigo_Final",
        "CajasPaletProdClte": "Cajas_Final"
    })

    # Merge para traer datos del producto final
    df_maestro = df_maestro.merge(
        df_lookup,
        on="ID_Final",
        how="left"
    )

    # Nos quedamos con las columnas finales limpias
    df_maestro_final = df_maestro[[
        "ID_ProdClte",
        "Codigo_Final",
        "Cajas_Final"
    ]].rename(columns={
        "Codigo_Final": "CodigoProdClte",
        "Cajas_Final": "CajasPaletProdClte"
    })

    df["Referencia"] = df["Referencia"].astype(str).str.strip()

    df = df.merge(
        df_maestro_final.rename(columns={"ID_ProdClte": "Referencia"}),
        on="Referencia",
        how="left"
    )

    df["CantidadLineaDoc"] = pd.to_numeric(df["CantidadLineaDoc"], errors="coerce")
    df["CajasPaletProdClte"] = pd.to_numeric(df["CajasPaletProdClte"], errors="coerce")

    df["Cajas"] = df["CantidadLineaDoc"] * df["CajasPaletProdClte"]
    

    nombre_archivo = f"{ddbb_name}_{date}.xlsx"
    df.to_excel(nombre_archivo, index=False)

    print(f"✅ Archivo generado correctamente: {nombre_archivo}")

    print(f"Hora de fin: {hora()}")
    engine.dispose()

if __name__ == "__main__":
    qry_inb_out(fecha_inicio, fecha_fin)