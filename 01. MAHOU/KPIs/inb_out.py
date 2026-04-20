from sqlalchemy import create_engine, text#type:ignore
import pandas as pd
from datetime import datetime

date = datetime.now().strftime("%Y%m%d%H%M%S")
ddbb_name = "KPIS_inb_out"
fecha_inicio = '2026-04-01'
fecha_fin = '2026-04-17'

def hora():
    hora = datetime.now().strftime("%H:%M:%S")
    return hora

def qry_inb_out(fecha_inicio, fecha_fin):
    ddbb_name = "KPIS_inb_out"

    print(f"Hora de inicio: {hora()}")

    # --- CONEXIÓN SQLALCHEMY ---

    engine = create_engine("mssql+pyodbc://@XGA_PROD")

    # --- QUERY SQL (rango de fechas) ---

    query_docs = text("""
        SELECT
            ID_Doc, NombreTipoDocumento AS 'Movimiento', FechaProcesoDoc AS 'Fecha', AlbaranDoc AS 'Documento', PaletsClienteDoc AS 'Palets', PesoFiege AS 'Peso', ObsEstado AS 'Observaciones'
        FROM
            vDocumentos
        WHERE
            ID_Cliente = 944
            AND ID_Almacen = 129
            AND (CodigoTipoDocumento = 'RS' OR CodigoTipoDocumento = 'ALB')
            AND CodigoTipoEstado IN ('040', '080', '085', '140', '130')
            AND CONVERT(date, FechaDoc) BETWEEN CONVERT(date, :inicio) AND CONVERT(date, :fin);

    """)

    #  ,PoblacionDireccion AS 'Poblacion', CampoCliente AS 'Tipo'

    # ---Ejecutamos la primera consulta ---
    with engine.connect() as conn:
        df_doc = pd.read_sql(query_docs, conn, params={"inicio": fecha_inicio, "fin": fecha_fin})

    

    # Normalizamos columnas clave
    df_doc["Movimiento"] = df_doc["Movimiento"].str.strip().str.upper()
    df_doc["Palets"] = pd.to_numeric(df_doc["Palets"], errors="coerce")

    # --Metemos en una lista los ID_Doc que nos interesan (ALB)
    ids_alb = (
        df_doc
        .loc[
            df_doc["Movimiento"].str.strip().str.upper() == "ALBARAN", "ID_Doc"]
        .dropna()
        .astype(str)
        .unique()
        .tolist()
    )
    for col in ["Fecha"]:
        if col in df_doc.columns:
            df_doc[col] = pd.to_datetime(df_doc[col], errors='coerce').dt.strftime("%d/%m/%Y").fillna("")

    #Query acotada a ID_Doc necesarios

    placeholders = ", ".join([f":id{i}" for i in range(len(ids_alb))])

    query_palets = text(f"""
        SELECT
            ID_Doc,
            CEILING(TotalPalets) AS Palets_Teoricos
        FROM
            vDocumentosPaletsTeoricos
        WHERE
            ID_Cliente = 944
            AND ID_Doc IN ({placeholders})
    """)


    # --- EJECUTAR  SEGUNDA CONSULTA CONSULTA ---

    with engine.connect() as conn:
        df_palets = pd.read_sql(query_palets, conn, params = {f"id{i}": v for i, v in enumerate(ids_alb)}
        )

    #HACEMOS MERGE DE LAS DOS CONSULTAS

    df = df_doc.merge(
        df_palets,
        on="ID_Doc",
        how="left"
    )

    # Solo para ALB, sustituimos Palets
    mask = (df["Movimiento"] == "ALBARAN") & df["Palets_Teoricos"].notna()

    df.loc[mask, "Palets"] = df.loc[mask, "Palets_Teoricos"]


    # Limpieza
    df.drop(columns=["Palets_Teoricos", "ID_Doc"], inplace=True)
    df["Palets"] = df["Palets"].astype("Int64")

    nombre_archivo = f"{ddbb_name}_{date}.xlsx"
    df.to_excel(nombre_archivo, index=False)

    print(f"✅ Archivo generado correctamente: {nombre_archivo}")

    print(f"Hora de fin: {hora()}")
    engine.dispose()

if __name__ == "__main__":
    qry_inb_out(fecha_inicio, fecha_fin)