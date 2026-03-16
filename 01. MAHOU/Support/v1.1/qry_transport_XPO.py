from sqlalchemy import create_engine, text # type:ignore
import pandas as pd  # type:ignore
import time
import difflib
import os

path = os.getcwd()

DB_FILE = f"{path}\\clientes.db"

def consulta_XPO(fecha_inicio, fecha_fin):

    # --- CONFIGURACIÓN GENERAL ---
    date = time.strftime("%Y%m%d%H%M%S")

    # --- CONEXIÓN SQL SERVER ---
    engine = create_engine("mssql+pyodbc://@XGA_PROD")
    
    # --- QUERY SQL ---
    query = text("""
        SELECT 
        RTRIM(AlbaranDoc) AS AlbaranDoc,
        '672487-GXO LOGISTICS SPAIN SLU' AS 'Sub-Account', 'SAN FERNANDO' AS 'Depot Information', RTRIM(AlbaranDoc) AS 'Customer Reference',
        'Taisa Logistics' AS 'Origin Address Reference', 'Taisa Logistics' AS 'Origin Address – Name', 'Av. la Veguilla, 20, Nave A' AS 'Origin Address Line 1',
        '' AS 'Origin Address Line 2', 'Cabanillas del Campo' AS 'Origin City', 'ES' as 'Origin – Country', 
        '19171' AS 'Origin – Zipcode', '' AS 'Pick up instructions', '' AS 'Pick up Date DD/MM/YYYY',
        'Before' AS 'Date Flexibility', '13:00' AS 'Pick up Time (HH:MM 24hr format)', 'Before' AS 'Time Flexibility',
        '' AS 'Destination Address Reference', RTRIM(NombreDireccion) AS 'Destination Address – Name', RTRIM(Direccion1Direccion) AS 'Destination Address Line 1',
        '' AS 'Destination - Address Line 2', PoblacionDireccion AS 'Destination City', 'ES' as 'Destination – Country',
        CodigoPostal AS 'Destination – Zipcode', ObsDocumento1 AS 'Delivery instructions', FechaProgramadaDoc AS 'Delivery Date DD/MM/YYYY',
        'Before' AS 'Delivery Date Flexibility', '22:00' AS 'Delivery Time (HH:MM 24hr format)', 'Before' AS 'Delivery Time Flexibility', RTRIM(AlbaranDoc) + '/' + PedidoDestinatarioDoc AS 'Special Instructions',
        'EUR' AS 'Commodity1', '1' AS 'Quantity1', ROUND(PesoFiege, 0) AS 'Weight1', ROUND(volumenFiege, 0) AS 'Volume1','' AS 'LinearMeter1',
        '' AS 'Commodity2', '' AS 'Quantity2', '' AS 'Weight2', '' AS 'Volume2','' AS 'LinearMeter2',
        '' AS 'Commodity3', '' AS 'Quantity3', '' AS 'Weight3', '' AS 'Volume3','' AS 'LinearMeter3',
        '' AS 'Commodity4', '' AS 'Quantity4', '' AS 'Weight4', '' AS 'Volume4','' AS 'LinearMeter4',
        '' AS 'Commodity5', '' AS 'Quantity5', '' AS 'Weight5', '' AS 'Volume5',
        '' AS 'Hazmat (Y/N)',
        '' AS 'UN #1', '' AS 'Label 1', '' AS 'Limited Quantity 1 (Y/N)', '' AS 'Packing Group 1','' AS 'Packages 1', '' AS 'Quantity 1', '' AS 'Size/Weight 1', '' AS 'UOM 1',
        '' AS 'UN #2', '' AS 'Label 2', '' AS 'Limited Quantity 2 (Y/N)', '' AS 'Packing Group 2','' AS 'Packages 2', '' AS 'Quantity 2', '' AS 'Size/Weight 2', '' AS 'UOM 2',
        '' AS 'UN #3', '' AS 'Label 3', '' AS 'Limited Quantity 3 (Y/N)', '' AS 'Packing Group 3','' AS 'Packages 3', '' AS 'Quantity 3', '' AS 'Size/Weight 3', '' AS 'UOM 3',
        '' AS 'UN #4', '' AS 'Label 4', '' AS 'Limited Quantity 4 (Y/N)', '' AS 'Packing Group 4','' AS 'Packages 4', '' AS 'Quantity 4', '' AS 'Size/Weight 4', '' AS 'UOM 4',
        '' AS 'UN #5', '' AS 'Label 5', '' AS 'Limited Quantity 5 (Y/N)', '' AS 'Packing Group 5','' AS 'Packages 5', '' AS 'Quantity 5', '' AS 'Size/Weight 5', '' AS 'UOM 5', 
        '' AS 'LinearMeter5',
        '' AS 'Booking In(Y/N)', '' AS 'Contact Name', '' AS 'Telephone Number', '' AS 'Installation', '' AS 'Assembly', '' AS 'Return Rate','' AS 'Haulage',
        '' AS 'Origin Contact Name', '' AS 'Origin Contact Number', '' AS 'Origin Contact Email Address', '' AS 'Origin Send Tracking Link Email(Y/N)',
        '' AS 'Destination Contact Name', '' AS 'Destination Contact Number', '' AS 'Destination Contact Email Address', ''  AS 'Destination Send Tracking Link Email(Y/N)',
        '' AS 'Origin Contact Name(2)', '' AS 'Origin Contact Number(2)', '' AS 'Origin Contact Email Address(2)', '' AS 'Origin Send Tracking Link Email(2) (Y/N)',
        '' AS 'Destination Contact Name(2)', '' AS 'Destination Contact Number(2)', '' AS 'Destination Contact Email Address(2)', ''  AS 'Destination Send Tracking Link Email(2) (Y/N)',
        '' AS 'Origin Contact Name(3)', '' AS 'Origin Contact Number(3)', '' AS 'Origin Contact Email Address(3)', '' AS 'Origin Send Tracking Link Email(3) (Y/N)',
        '' AS 'Destination Contact Name(3)', '' AS 'Destination Contact Number(3)', '' AS 'Destination Contact Email Address(3)', ''  AS 'Destination Send Tracking Link Email(3) (Y/N)',
        '' AS 'Origin Contact Name(4)', '' AS 'Origin Contact Number(4)', '' AS 'Origin Contact Email Address(4)', '' AS 'Origin Send Tracking Link Email(4) (Y/N)',
        '' AS 'Destination Contact Name(4)', '' AS 'Destination Contact Number(4)', '' AS 'Destination Contact Email Address(4)', ''  AS 'Destination Send Tracking Link Email(4) (Y/N)',
        '' AS 'Origin Contact Name(5)', '' AS 'Origin Contact Number(5)', '' AS 'Origin Contact Email Address(5)', '' AS 'Origin Send Tracking Link Email(5) (Y/N)',
        '' AS 'Destination Contact Name(5)', '' AS 'Destination Contact Number(5)', '' AS 'Destination Contact Email Address(5)', ''  AS 'Destination Send Tracking Link Email(5) (Y/N)'


        FROM
        vDocumentos
    WHERE 
        ID_Cliente = 944
        AND (NombreTipoDocumento = 'Albaran' OR NombreTipoDocumento = 'Recogida')
        AND (RutaReparto = 'MSMCABXPO' OR RutaReparto = 'MSMALOXPO')
        AND CONVERT(date, FechaDoc) BETWEEN CONVERT(date, :inicio) AND CONVERT(date, :fin) 

    """)
    #
    query_pend = text("""
    SELECT 
        RTRIM(AlbaranDoc) AS AlbaranDoc,
        FechaTeoricaCargaDoc AS [Pick up Date DD/MM/YYYY]
    FROM 
        Documentos
    WHERE 
        ID_Cliente = 944
        AND (ID_TipoDocumento = 1 OR ID_TipoDocumento = 2)
        AND CONVERT(date, FechaDoc) BETWEEN CONVERT(date, :inicio) AND CONVERT(date, :fin)
    """)

# --- EJECUTAR CONSULTA SQL SERVER ---
    with engine.connect() as conn:
        df_doc = pd.read_sql(query, conn, params={"inicio": fecha_inicio, "fin": fecha_fin})
        df_pend = pd.read_sql(query_pend, conn, params={"inicio": fecha_inicio, "fin": fecha_fin})

    # --- LIMPIAR COLUMNAS ---
    df_doc.columns = df_doc.columns.str.strip()
    df_pend.columns = df_pend.columns.str.strip()
    df_doc["AlbaranDoc"] = df_doc["AlbaranDoc"].astype(str).str.strip()
    df_pend["AlbaranDoc"] = df_pend["AlbaranDoc"].astype(str).str.strip()

    # --- UNIR TABLAS DE SQL SERVER ---
    df = df_doc.merge(df_pend, on="AlbaranDoc", how="left")
    if "Pick up Date DD/MM/YYYY_y" in df.columns:
        df["Pick up Date DD/MM/YYYY"] = df["Pick up Date DD/MM/YYYY_y"]
        df = df.drop(columns=[col for col in df.columns if col.endswith(("_x", "_y"))])

    # Insertar Delivery Date después de Delivery Instructions
    if "Pick up Date DD/MM/YYYY" in df.columns and "Pick up instructions" in df.columns:
        idx = df.columns.get_loc("Pick up instructions") + 1 #type:ignore
        col = df.pop("Pick up Date DD/MM/YYYY")
        df.insert(idx, "Pick up Date DD/MM/YYYY", col)#type:ignore

    df.drop(columns=["AlbaranDoc"], inplace=True)
    
    # --- FORMATEAR FECHAS ---
    for col in ["Pick up Date DD/MM/YYYY", "Delivery Date DD/MM/YYYY"]:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors='coerce').dt.strftime("%d/%m/%Y").fillna("")

    # --- CONEXIÓN SQLITE ---
    
    engine_sqlite = create_engine(f"sqlite:///{DB_FILE}")
    df_aux = pd.read_sql("SELECT * FROM direcciones_clientes", engine_sqlite)
    df_aux.columns = df_aux.columns.str.strip().str.upper()

    col_nombre = "Destination Address – Name"
    col_line1 = "Destination Address Line 1"

    # --- NORMALIZAR STRINGS ---
    for col in ["ABALPH", "ALADD1", "ALAN8"]:
        df_aux[col] = df_aux[col].astype(str).str.strip().str.upper()
    df[col_nombre] = df[col_nombre].astype(str).str.strip().str.upper()
    df[col_line1] = df[col_line1].astype(str).str.strip().str.upper()

    # --- RELLENAR DESTINATION ADDRESS REFERENCE ---
    df["Destination Address Reference"] = None
    
    # Match exacto ABALPH
    df_abalph = df_aux.drop_duplicates(subset="ABALPH").set_index("ABALPH")["ALAN8"].to_dict()
    for idx, nombre in df[col_nombre].items():
        clave = nombre.strip().upper()
        if clave in df_abalph:
            df.at[idx, "Destination Address Reference"] = df_abalph[clave]#type:ignore

    # Match exacto ALADD1
    faltan = df["Destination Address Reference"].isna()
    df_aladd1 = df_aux.drop_duplicates(subset="ALADD1").set_index("ALADD1")["ALAN8"].to_dict()
    for idx in df[faltan].index:
        clave = df.at[idx, col_line1].strip().upper()#type:ignore
        if clave in df_aladd1:
            df.at[idx, "Destination Address Reference"] = df_aladd1[clave]

    # Fuzzy match con ABALPH
    faltan = df["Destination Address Reference"].isna()
    lista_abalph = df_aux["ABALPH"].tolist()
    for idx in df[faltan].index:
        nombre = df.at[idx, col_nombre].strip()#type:ignore
        matches = difflib.get_close_matches(nombre, lista_abalph, n=1, cutoff=0.6)
        if matches:
            df.at[idx, "Destination Address Reference"] = df_aux.loc[df_aux["ABALPH"]==matches[0], "ALAN8"].values[0]

    # --- EXPORTAR A EXCEL ---
    nombre_archivo = f"XPO_{fecha_inicio}_{fecha_fin}_{date}.xlsx"
    df.to_excel(nombre_archivo, index=False, sheet_name="Template")
 

    engine.dispose()
    engine_sqlite.dispose()


if __name__ == "__main__":
    consulta_XPO("2025-11-27", "2025-12-01")