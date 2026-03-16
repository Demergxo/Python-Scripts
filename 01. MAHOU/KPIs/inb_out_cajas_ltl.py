from sqlalchemy import create_engine, text#type:ignore
import pandas as pd
from datetime import datetime
import time
import os

path = os.getcwd()
DB_FILE = f"{path}\\apoyo.db"
usuario = os.environ['USERNAME']

archive = f"C:\\Users\\{usuario}\\OneDrive - GXO\\Escritorio\\KPIS Transporte MSM.xlsx"

date = datetime.now().strftime("%Y%m%d%H%M%S")
ddbb_name = "KPIS_inb_out_cajas_ltl"
fecha_inicio = '2026-03-09'
fecha_fin = '2026-03-15'

def chunks(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i:i+n]

def leer_excel(archivo):
    df = pd.read_excel(archivo,
    usecols = ["Fecha Expedición", "Tipo Doc", "Nº Documento", "On Time", "Incidencia", "Cantidad de Artículos", "Responsable", "Observaciones"]
    )
    #df_filtrado = df[df["Tipo Doc"] != "REC"]
    df_filtrado = df[~df["Tipo Doc"].isin(["REC", "DEV"])]
    df_filtrado = df_filtrado.rename(columns={"Nº Documento": "AlbaranDoc"})
    df_filtrado["AlbaranDoc"] = df_filtrado["AlbaranDoc"].astype(str).str.strip()
    
    return df_filtrado
    #print(df_filtrado)

def hora():
    hora = datetime.now().strftime("%H:%M:%S")
    return hora

def qry_inb_out_ltl():

    print(f"Hora de inicio: {hora()}")
    df_xlsx = leer_excel(archive)

    list_alb = df_xlsx["AlbaranDoc"].tolist()
    if not list_alb:
        print("⚠️ No se encontraron albaranes en el archivo")
        return
    
    placeholders_1 = ", ".join([f"'{i}'" for i in list_alb])

    # --- CONEXIÓN SQLALCHEMY ---

    engine = create_engine("mssql+pyodbc://@XGA_PROD")

    # --- QUERY SQL (rango de fechas) ---

    query_docs = text(f"""
        SELECT
            ID_Doc, AlbaranDoc, PesoFiege
        FROM
            vDocumentos
        WHERE
            ID_Cliente = 944
            AND ID_Almacen = 220
            AND CodigoTipoDocumento = 'ALB'
            AND AlbaranDoc IN ({placeholders_1})
            
    """)

    

    #  ,PoblacionDireccion AS 'Poblacion', CampoCliente AS 'Tipo'

    # ---Ejecutamos la primera consulta ---
    with engine.connect() as conn:
        df_doc = pd.read_sql(query_docs, conn, params={f"id{i}": v for i, v in enumerate(list_alb)})

        # Normalizamos columnas clave
    df_doc["AlbaranDoc"] = df_doc["AlbaranDoc"].str.strip()
    df_doc = df_doc.merge(
            df_xlsx,
            on="AlbaranDoc",
            how="left"
    )
        
    list_ids = df_doc["ID_Doc"].tolist()

    #Query acotada a ID_Doc necesarios
    if not list_ids:
        print("⚠️ No se encontraron documentos en ese rango")
        return

    dfs =[]

    placeholders = ", ".join([f":id{i}" for i in range(len(list_ids))])

    #Query acotada a ID_Doc necesarios

    with engine.connect() as conn:
        for chunk in chunks(list_ids, 1000):

            placeholders = ", ".join([f":id{i}" for i in range(len(chunk))])

            query_dos = text(f"""
                SELECT
                    ID_Doc, ID_ProdClte, CantidadLineaDoc, ID_IncidenciaLinea
                FROM
                    vLineasDocumentos
                WHERE
                    ID_Cliente = 944
                    AND ID_Almacen = 220
                    AND TipoMovimientoLineaDoc = 'S'
                    AND ID_Doc IN ({placeholders})
            """)

            params = {f"id{i}": v for i, v in enumerate(chunk)}

            df_chunk = pd.read_sql(query_dos, conn, params=params)

            dfs.append(df_chunk)

        df_palets = pd.concat(dfs, ignore_index=True)

    #HACEMOS MERGE DE LAS DOS CONSULTAS
    
    df = df_doc.merge(
        df_palets,
        on="ID_Doc",
        how="left"
    )

    df["ID_ProdClte"] = pd.to_numeric(df["ID_ProdClte"], errors="coerce").fillna(0).astype(int).astype(str)

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

    df["ID_ProdClte"] = df["ID_ProdClte"].astype(str).str.strip()

    df = df.merge(
        df_maestro_final,
        on="ID_ProdClte",
        how="left"
    )

    df["CantidadLineaDoc"] = pd.to_numeric(df["CantidadLineaDoc"], errors="coerce")
    df["CajasPaletProdClte"] = pd.to_numeric(df["CajasPaletProdClte"], errors="coerce")

    df["Cajas"] = df["CantidadLineaDoc"] * df["CajasPaletProdClte"]

    df_group = df_group = (
        df
        .groupby(["AlbaranDoc", "Tipo Doc"], as_index=False)
        .agg({
            "Fecha Expedición": "first",
            "On Time": "first",
            "Cajas": "sum",
            "PesoFiege": "sum",
            "Cantidad de Artículos": "first",
            "Incidencia": "first",
            "Responsable": "first",
            "Observaciones": "first"
        })    )
    

    nombre_archivo = f"{ddbb_name}_{date}.xlsx"
    df_group.to_excel(nombre_archivo, index=False)

    print(f"✅ Archivo generado correctamente: {nombre_archivo}")

    print(f"Hora de fin: {hora()}")
    engine.dispose()

if __name__ == "__main__":
    qry_inb_out_ltl()