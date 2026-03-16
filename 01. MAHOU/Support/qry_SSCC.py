from sqlalchemy import create_engine, text #type:ignore
import pandas as pd
import time
from datetime import datetime

def hora():
    hora = datetime.now().strftime("%H:%M:%S")
    return hora

def sacar_sscc(fecha_inicio, fecha_fin):
    # --- CONFIGURACIÓN GENERAL ---
    date = time.strftime("%Y%m%d%H%M%S")
    print("")
    print("-"*32)
    print(f"\nIniciado a: {hora()}\n")

    # --- CONEXIÓN SQLALCHEMY ---
    # ⚠️ Ajusta tu DSN o credenciales según tu entorno
    engine = create_engine("mssql+pyodbc://@XGA_PROD")

    # --- QUERY SQL (rango de fechas) ---
    query = text("""
        SELECT
            ID_Doc, AlbaranDoc AS 'Albarán', FechaDoc AS 'Fecha Integración', PesoFiege AS 'Peso Teórico', volumenFiege AS 'Volumen Teórico'
        FROM
            vDocumentos
        WHERE
            ID_Cliente = 944
            AND NombreTipoDocumento = 'Albaran'
            AND CONVERT(date, FechaDoc) BETWEEN CONVERT(date, :inicio) AND CONVERT(date, :fin)
    """)

    query_sscc = text("""
        SELECT 
            ID_Doc, CantidadMvtoPalet AS 'Unidades Requeridas', CantidadConfirmadaMvtoPalet AS 'Unidades Enviadas',  SSCCPalet AS 'SSCC'

        FROM
            vLineasDocumentosPreparadas
        WHERE 
            ID_Cliente = 944                  
                            
    """)

    query_aux = text("""
        SELECT
            CodigoProdClte AS 'Referencia', NombreProdClte AS 'Nombre Producto', SSCCPaletPicking AS 'SSCC'
        FROM
            vLineasDocumentosLotesServidosconSSCCPicking
        WHERE
            ID_Cliente = 944

    """)

    # --- EJECUTAR CONSULTA ---
    with engine.connect() as conn:
        df_doc = pd.read_sql(query, conn, params={"inicio": fecha_inicio, "fin": fecha_fin})
        df_sscc = pd.read_sql(query_sscc, conn)
        df_aux =pd.read_sql(query_aux, conn)

    # --- LIMPIAR COLUMNAS ---
    for df_temp in (df_doc, df_sscc, df_aux):
        if "ID_Doc" in df_temp.columns:
            df_temp["ID_Doc"] = df_temp["ID_Doc"].astype(str).str.strip()

    # --- UNIR POR ID_Doc ---
    df = df_doc.merge(df_sscc, on="ID_Doc", how="left")
    if "Albaran_y" in df.columns:
        df["Albaran"] = df["Albaran_y"]
    elif "Albaran" not in df.columns and "AlbaranDoc" in df.columns:
        df["Albaran"] = df["AlbaranDoc"]

    # ---UNIR POR SSCC---
    df = df.merge(df_aux, on="SSCC", how="left")
    if "SSCC_y" in df.columns:
        df["SSCC"] = df["SSCC_y"]
        df = df.drop(columns=[col for col in df.columns if col.endswith(("_x", "_y"))])

    # --- EXPORTAR ---
    nombre_archivo = f"SSCC_{fecha_inicio}_a_{fecha_fin}_{date}.xlsx"
    df.to_excel(nombre_archivo, index=False)

    print("")
    print("-"*32)
    print(f"✅ Archivo generado correctamente: {nombre_archivo}")
    print("")
    print("-"*32)
    print(f"\nFinalizado a: {hora()}")
    engine.dispose()


if __name__ == "__main__":
    fecha_inicio = str(input("\nIngrese fecha inicio (YYYY-MM-DD): "))
    fecha_final = str(input("Ingrese fecha final (YYYY-MM-DD): "))
    sacar_sscc(fecha_inicio, fecha_final)

