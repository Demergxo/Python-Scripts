from sqlalchemy import create_engine, text#type:ignore
import pandas as pd
from datetime import datetime


date = datetime.now().strftime("%Y%m%d%H%M%S")
ddbb_name = "KPIS_roturas_stock"
fecha_inicio = '2026-03-01'
fecha_fin = '2026-03-08' 

def hora():
    hora = datetime.now().strftime("%H:%M:%S")
    return hora

def qry_inb_out(fecha_inicio, fecha_fin):
    date = datetime.now().strftime("%Y%m%d%H%M%S")
    ddbb_name = "KPIS_roturas_stock"

    print(f"Hora de inicio: {hora()}")

    # --- CONEXIÓN SQLALCHEMY ---

    engine = create_engine("mssql+pyodbc://@XGA_PROD")

    # --- QUERY SQL (rango de fechas) ---

    query_docs = text("""
        SELECT
            ID_Doc, AlbaranDoc AS Documento, FechaProcesoDoc AS Fecha
        FROM
            vDocumentos
        WHERE
            ID_Cliente = 944
            AND ID_Almacen = 129
            AND CodigoTipoDocumento = 'AJU'
            AND (
                    CodigoTipoAjuste IN ('AME', 'AX9')
                    OR (CodigoTipoAjuste = 'AUJ' AND ID_TipoAjuste = 1276)
                )
            AND CONVERT(date, FechaProcesoDoc) BETWEEN CONVERT(date, :inicio) AND CONVERT(date, :fin);

    """)

    

    # ---Ejecutamos la primera consulta ---
    with engine.connect() as conn:
        df_doc = pd.read_sql(query_docs, conn, params={"inicio": fecha_inicio, "fin": fecha_fin})

    
    # --Metemos en una lista los ID_Doc 
    
    list_ids = df_doc["ID_Doc"].tolist()

    #Query acotada a ID_Doc necesarios

    placeholders = ", ".join([f":id{i}" for i in range(len(list_ids))])

    query_palets = text(f"""
        SELECT
            ID_Doc,
            CEILING(CAST(PesoBrutoProdClte AS FLOAT)) AS Peso, CodigoProdClte, CantidadLineaDoc

        FROM
            vLineasDocumentosConsulta
        WHERE
            ID_Cliente = 944
            AND ID_Almacen = 129
            AND CodigoDeposito = '000'
            AND TipoMovimientoLineaDoc = 'S'
            AND ID_Doc IN ({placeholders})
    """)


    # --- EJECUTAR  SEGUNDA CONSULTA CONSULTA ---

    with engine.connect() as conn:
        df_palets = pd.read_sql(query_palets, conn, params = {f"id{i}": v for i, v in enumerate(list_ids)}
        )

    # Solo un registro por ID_Doc con el sumatorio de peso
    df_palets_agg = (
        df_palets
        .groupby("ID_Doc", as_index=False)["Peso"]
        .sum()
    )

    #HACEMOS MERGE DE LAS DOS CONSULTAS

    df = df_doc.merge(
        df_palets_agg,
        on="ID_Doc",
        how="left"
    )

    # Limpieza
    df.drop(columns=["ID_Doc"], inplace=True)
    

    nombre_archivo = f"{ddbb_name}_{date}.xlsx"
    df.to_excel(nombre_archivo, index=False)

    print(f"✅ Archivo generado correctamente: {nombre_archivo}")

    print(f"Hora de fin: {hora()}")
    engine.dispose()

if __name__ == "__main__":
    qry_inb_out(fecha_inicio, fecha_fin)