from sqlalchemy import create_engine, text #type:ignore
import pandas as pd
import time
import os
#import pyodbc
#print(pyodbc.drivers())

path = os.getcwd()

DB_FILE = f"{path}\\clientes.db"
print(path)

def consulta_taisa(fecha_inicio, fecha_fin):
    # --- CONFIGURACIÓN GENERAL ---
    date = time.strftime("%Y%m%d%H%M%S")
    
    # --- Conexión SQL Server ---
   
    engine = create_engine("mssql+pyodbc://@XGA_PROD")

    # --- QUERY SQL (rango de fechas) ---
    query = text("""
        SELECT 
        '' AS 'Fecha Expedición', FechaProgramadaDoc AS 'Fecha Requerida', ObsDocumento1 AS 'Horario Descarga', '' AS 'Instrucciones de entrega',
        '' AS 'Agrupación carga / Matrícula', '' AS 'Hora de Carga',NombreTipoDocumento AS 'Tipo', CampoCliente AS 'Tipo Doc', RTRIM(AlbaranDoc) AS 'AlbaranDoc', PedidoDestinatarioDoc AS 'Pedido Cliente',
        CodigoDireccion AS 'Cliente Envío', NombreDireccion AS 'Descripción Cliente Envío', PoblacionDireccion AS 'Población',CodigoPostal AS 'Código Postal', 
        Direccion1Direccion AS 'Dirección de entrega', ROUND(PesoFiege, 2) AS 'Peso Bruto', CEILING(PesoFiege / 700.0) AS 'Palés', '527' AS 'Estado', '' AS 'Peso Facturable (Real Taisa)',
        '' AS 'Palés Reales Taisa', '' AS 'Bases Reales Taisa', '8180' AS 'Almacén', '' AS 'Canal', RTRIM(RutaReparto) AS 'Transporte'
    FROM
        vDocumentos 
    WHERE 
        ID_Cliente = 944
        AND (NombreTipoDocumento = 'Albaran' OR NombreTipoDocumento = 'Recogida')
        
        AND CONVERT(date, FechaProcesoDoc) BETWEEN CONVERT(date, :inicio) AND CONVERT(date, :fin) 
    """)
    #ND ID_Almacen = 220

    query_pend = text("""
    SELECT
        AlbaranDoc ,FechaTeoricaCargaDoc AS 'Fecha Expedición'
    FROM 
        Documentos
    WHERE 
        ID_Cliente = 944
        AND (ID_TipoDocumento = 1 OR ID_TipoDocumento = 2)
        AND CONVERT(date, FechaDoc) BETWEEN CONVERT(date, :inicio) AND CONVERT(date, :fin)


    """)

    
    
    # --- EJECUTAR CONSULTA ---
    with engine.connect() as conn:
        df_doc = pd.read_sql(query, conn, params={"inicio": fecha_inicio, "fin": fecha_fin})
        df_pend = pd.read_sql(query_pend, conn, params={"inicio": fecha_inicio, "fin": fecha_fin})
    
    # --- LIMPIAR COLUMNAS ---
    for df_temp in (df_doc, df_pend):
        if "AlbaranDoc" in df_temp.columns:
            df_temp["AlbaranDoc"] = df_temp["AlbaranDoc"].astype(str).str.strip()

    # --- UNIR POR AlbaranDoc ---
    df = df_doc.merge(df_pend, on="AlbaranDoc", how="left")
    if "Fecha Expedición_y" in df.columns:
        df["Fecha Expedición"] = df["Fecha Expedición_y"]
        df = df.drop(columns=[c for c in df.columns if c.endswith(("_x", "_y"))], errors="ignore")


    
    # --- Quitar ceros a la izquierda de 'Cliente Envío' ---
    if "Cliente Envío" in df.columns:
        df["Cliente Envío"] = df["Cliente Envío"].astype(str).str.lstrip("0")
        
    # --- Cambiar nombre final de columna AlbaranDoc ---
    if "AlbaranDoc" in df.columns:
        df = df.rename(columns={"AlbaranDoc": "Nº Documento"})
        
    # Insertar Tipo Doc después de Hora de Carga
    if "Fecha Expedición" in df.columns:
        
        col = df.pop("Fecha Expedición")
        df.insert(0, "Fecha Expedición", col) #type:ignore
        
    
    # --- FORMATEAR FECHAS ---
    for col in ["Fecha Expedición", "Fecha Requerida"]:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors='coerce').dt.strftime("%d/%m/%Y").fillna("")
    
    # --- CONEXIÓN SQLITE ---
    engine_sqlite = create_engine(f"sqlite:///{DB_FILE}")
    df_aux = pd.read_sql("SELECT * FROM canal_msm", engine_sqlite)
    
    # print("📘 Columnas del dataframe principal:", df.columns.tolist())
    # print("📗 Columnas en canal_msm:", df_aux.columns.tolist())
    
    # --- Normalizar columnas ---
    df_aux.columns = df_aux.columns.str.strip().str.upper()
    df.columns = df.columns.str.strip().str.upper()

    # print("📘 Columnas normalizadas (df):", df.columns.tolist())
    # print("📗 Columnas normalizadas (canal_msm):", df_aux.columns.tolist())

    # --- Asegurar que existan las columnas necesarias ---
    # if "TIPO DOC" not in df.columns:
    #     print("⚠️ No se encontró la columna 'Tipo Doc' en el dataframe principal.")
    #     return
    # if not {"NOMBRE", "CANAL"}.issubset(df_aux.columns):
    #     print("⚠️ La tabla canal_msm no contiene las columnas 'Nombre' y 'Canal'.")
    #     return

    # --- Normalizar valores ---
    df_aux["NOMBRE"] = df_aux["NOMBRE"].astype(str).str.strip().str.upper()
    df_aux["CANAL"] = df_aux["CANAL"].astype(str).str.strip().str.upper()
    df["TIPO DOC"] = df["TIPO DOC"].astype(str).str.strip().str.upper()
   

    
    # --- Mapear Tipo Doc -> Canal según canal_msm ---
    mapa_canal = df_aux.drop_duplicates(subset="NOMBRE").set_index("NOMBRE")["CANAL"].to_dict()
    df["CANAL"] = df["TIPO DOC"].map(mapa_canal)

    # --- Mostrar resumen del mapeo ---
    #n_coinciden = df["CANAL"].notna().sum()
    #print(f"✅ Coincidencias encontradas: {n_coinciden} / {len(df)}")

    #faltantes = df[df["CANAL"].isna()]["TIPO DOC"].unique().tolist()
    # if faltantes:
    #     print("⚠️ Tipo Doc sin coincidencia en canal_msm:", faltantes[:10], "...")  # muestra los primeros 10

    # --- Mover Canal a penúltima posición ---
    if "CANAL" in df.columns:
        col = df.pop("CANAL")
        df.insert(len(df.columns), "CANAL", col)
    
    # --- Ajustar valor de Transporte ---
    if "TRANSPORTE" in df.columns:
        df["TRANSPORTE"] = df["TRANSPORTE"].astype(str).str.strip().str.upper()
        df.loc[df["TRANSPORTE"] == "MSMCABXPO", "TRANSPORTE"] = "XPO"
        df.loc[df["TRANSPORTE"] == "CABSCHENKER", "TRANSPORTE"] = "SCHENKER"
        
        # --- Mover Transporte al final ---
        col = df.pop("TRANSPORTE")
        df.insert(len(df.columns), "TRANSPORTE", col)

    # --- Exportar ---
    nombre_archivo = f"Facturacion_{fecha_inicio}_{fecha_fin}_{date}.xlsx"
    df.to_excel(nombre_archivo, index=False)
    #print(f"✅ Archivo generado correctamente: {nombre_archivo}")
    engine.dispose()
    
if __name__ == "__main__":
    consulta_taisa("2026-01-16", "2026-01-21")