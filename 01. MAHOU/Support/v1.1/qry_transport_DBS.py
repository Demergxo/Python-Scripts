from sqlalchemy import create_engine, text
import pandas as pd 
import time
import difflib
import os

path = os.getcwd()

DB_FILE = f"{path}\\clientes.db"

def consulta_DBS(fecha_inicio, fecha_fin):

    # --- CONFIGURACIÓN GENERAL ---
    date = time.strftime("%Y%m%d%H%M%S")

    # --- CONEXIÓN SQL SERVER ---
    engine = create_engine("mssql+pyodbc://@XGA_PROD")
    
    # --- QUERY SQL ---
    query = text("""
SELECT 
    AlbaranDoc,
    'Taisa Logistics' AS 'NOMBRE_RECOGIDA','' AS 'NOMBRE_RECOGIDA_AMPLIADO', 'Avda. de la Veguilla, 20, Nave A' AS 'DIRECCION_RECOGIDA',
    '' AS 'DIRECCION_RECOGIDA_AMPLIADA', '1971' AS 'CODIGO_POSTAL_RECOGIDA', 'Cabanillas del Campo' AS 'CIUDAD_RECOGIDA',
    'ES' as 'PAIS_RECOGIDA', '608717032' AS 'TELEFONO_RECOGIDA', 'oscar.comendadormendoza@gxo.com' AS 'MAIL_REMITENTE',NombreDireccion AS 'NOMBRE_DESTINATARIO',
    '' AS 'NOMBRE_DESTINATARIO_AMPLIADO', Direccion1Direccion AS 'DIRECCION_DESTINATARIO', '' AS 'DIRECCION_DESTINATARIO_AMPLIADA',
    CodigoPostal AS 'CODIGO_POSTAL_DESTINATARIO', PoblacionDireccion AS 'CIUDAD_DESTINATARIO', 'ES' AS 'PAIS_DESTINATARIO',
    '' AS 'TELEFONO_DESTINATARIO', '' AS 'MAIL_DESTINATARIO', 'DAP' AS 'INCOTERMS',
    PoblacionDireccion AS 'LOCALIDAD_INCOTERMS', '1' AS 'UNIDADES', 'PALET' AS 'TIPO_BULTO',
    ROUND(PesoFiege,2) AS 'PESO_TOTAL', '' AS 'LARGO', '' AS 'ANCHO',
    '' AS 'ALTO', ROUND(volumenFiege,3) AS 'VOLUMEN_TOTAL', 'BEBIDAS' AS 'DESCRIPCION_MERCANCIA',
    '' AS 'REFERENCIA_PRODUCTO', 'NO' AS 'REMONTABLE',  'PClte: ' + RTRIM(PedidoDestinatarioDoc) + ' / ' + RTRIM(ObsDocumento1) AS 'OBSERVACIONES',
    RTRIM(AlbaranDoc) AS 'REFERENCIA_GENERAL', '43' AS 'PRODUCTO', '' AS 'FECHA_RECOGIDA_DESDE',
    '' AS 'FECHA_RECOGIDA_HASTA','SI' AS 'FIXDAY', FechaProgramadaDoc AS 'FECHA',
    '' AS 'PRENOTICE_CONTACT_NAME', '' AS 'PRENOTICE_MAIL', '' AS 'CONTACT_FDTBA_NAME',
    '' AS 'TELEFONO_FDTBA', '' AS 'FIXDAY_TO_BE_AGREED_AUTOMATED', '' AS 'ADUANAS',
    '' AS 'VALOR_MERCANCIA', '' AS 'VALOR_SEGURO', '' AS 'VALOR_CONTRAREMBOLSO',
    '' AS 'ADR', '' AS 'N_BULTOS', '' AS 'TIPO_BULTO',
    '' AS 'PESO', '' AS 'UNIDAD_MEDIDA', '' AS 'BASE_PONDERAL',
    '' AS 'UN_ID', '' AS 'N_ETIQUETA', '' AS 'GRUPO_BULTOS',
    '' AS 'NOMBRE_ENVIO_ADECUADO', '' AS ' NOMBRE_TECNICO', '' AS 'DISPOSICION_ESPECIAL',
    '' AS 'CODIGO_TUNEL', '' AS 'NEM', '' AS 'TRANSPORT_CATEGORY', 
    '' AS 'RESIDUOS', '' AS 'CODIGO_EUROPEO_RESIDUOS', '' AS 'CANTIDAD_EXENTA',
    '' AS 'CANTIDAD_LIMITADA', '' AS 'PELIGROSIDAD_ENTORNO',
    '' AS 'EXTRA_1', '' AS 'EXTRA_2', '' AS 'EXTRA_3', '' AS 'EXTRA_4', '' AS 'EXTRA_5', '' AS 'EXTRA_6', 
    '' AS 'EXTRA_7', '' AS 'EXTRA_8', '' AS 'EXTRA_9', '' AS 'EXTRA_10', '' AS 'EXTRA_11', '' AS 'EXTRA_12', 
    '' AS 'EXTRA_13', '' AS 'EXTRA_14', '' AS 'EXTRA_15', '' AS 'EXTRA_16', '' AS 'EXTRA_17', '' AS 'EXTRA_18', 
    '' AS 'EXTRA_19', '' AS 'EXTRA_20' 

FROM
    vDocumentos

WHERE 
    ID_Cliente = 944
    AND (NombreTipoDocumento = 'Albaran' OR NombreTipoDocumento = 'Recogida')
    AND (RutaReparto = 'CABSCHENKER' OR OR RutaReparto = 'SCHENKER')
    AND CONVERT(date, FechaDoc) BETWEEN CONVERT(date, :inicio) AND CONVERT(date, :fin);

    """)
#

    query_pend = text("""
SELECT
    AlbaranDoc ,FechaTeoricaCargaDoc AS 'FECHA_RECOGIDA_DESDE', FechaTeoricaCargaDoc AS 'FECHA_RECOGIDA_HASTA'
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


    # --- Unit Tablas SQL ----
    df = df_doc.merge(df_pend, on="AlbaranDoc", how="left")

    # Renombrar columnas si existen
    if "FECHA_RECOGIDA_DESDE_y" in df.columns:
        df["FECHA_RECOGIDA_DESDE"] = df["FECHA_RECOGIDA_DESDE_y"]

    if "FECHA_RECOGIDA_HASTA_y" in df.columns:
        df["FECHA_RECOGIDA_HASTA"] = df["FECHA_RECOGIDA_HASTA_y"]

    # Eliminar columnas duplicadas (_x, _y)
    df = df.drop(columns=[col for col in df.columns if col.endswith(("_x", "_y"))])

    # Reordenar columnas
    if "FECHA_RECOGIDA_DESDE" in df.columns and "PRODUCTO" in df.columns:
        idx = df.columns.get_loc("PRODUCTO") + 1 #type: ignore
        col = df.pop("FECHA_RECOGIDA_DESDE")
        df.insert(idx, "FECHA_RECOGIDA_DESDE", col)#type: ignore

    if "FECHA_RECOGIDA_DESDE" in df.columns and "FECHA_RECOGIDA_HASTA" in df.columns:
        idx = df.columns.get_loc("FECHA_RECOGIDA_DESDE") + 1 #type: ignore
        col = df.pop("FECHA_RECOGIDA_HASTA")
        df.insert(idx, "FECHA_RECOGIDA_HASTA", col)#type: ignore

    # Eliminar columna clave si no la necesitas
    df.drop(columns=["AlbaranDoc"], inplace=True)


    # --- FORMATEAR FECHAS ---
    for col in ["FECHA_RECOGIDA_DESDE", "FECHA", "FECHA_RECOGIDA_HASTA"]:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors='coerce').dt.strftime("%d/%m/%Y").fillna("")

    # --- CONEXIÓN SQLITE ---
    
    engine_sqlite = create_engine(f"sqlite:///{DB_FILE}")
    df_aux = pd.read_sql("SELECT * FROM direcciones_clientes", engine_sqlite)
    df_aux.columns = df_aux.columns.str.strip().str.upper()

    col_nombre = "NOMBRE_DESTINATARIO"
    col_line1 = "DIRECCION_DESTINATARIO"

    
    # --- NORMALIZAR STRINGS ---
    for col in ["ABALPH", "ALADD1", "ALAN8"]:
        df_aux[col] = df_aux[col].astype(str).str.strip().str.upper()
    df[col_nombre] = df[col_nombre].astype(str).str.strip().str.upper()
    df[col_line1] = df[col_line1].astype(str).str.strip().str.upper()

    # --- RELLENAR DESTINATION ADDRESS REFERENCE ---
    df["EXTRA_1"] = None

    # Match exacto ABALPH
    df_abalph = df_aux.drop_duplicates(subset="ABALPH").set_index("ABALPH")["ALAN8"].to_dict()
    for idx, nombre in df[col_nombre].items():
        clave = nombre.strip().upper()
        if clave in df_abalph:
            df.at[idx, "EXTRA_1"] = df_abalph[clave]#type:ignore

    # Match exacto ALADD1
    faltan = df["EXTRA_1"].isna()
    df_aladd1 = df_aux.drop_duplicates(subset="ALADD1").set_index("ALADD1")["ALAN8"].to_dict()
    for idx in df[faltan].index:
        clave = df.at[idx, col_line1].strip().upper()#type:ignore
        if clave in df_aladd1:
            df.at[idx, "EXTRA_1"] = df_aladd1[clave]

    # Fuzzy match con ABALPH
    faltan = df["EXTRA_1"].isna()
    lista_abalph = df_aux["ABALPH"].tolist()
    for idx in df[faltan].index:
        nombre = df.at[idx, col_nombre].strip()#type:ignore
        matches = difflib.get_close_matches(nombre, lista_abalph, n=1, cutoff=0.6)
        if matches:
            df.at[idx, "EXTRA_1"] = df_aux.loc[df_aux["ABALPH"]==matches[0], "ALAN8"].values[0]


    # --- EXPORTAR A CSV ---
    nombre_archivo = f"DSV_{fecha_inicio}_{fecha_fin}_{date}.csv"
    df.to_csv(nombre_archivo, index=False, sep=";", encoding='utf-8-sig')
    #print(f"✅ Archivo CSV generado correctamente: {nombre_archivo}")

    engine.dispose()
    engine_sqlite.dispose()


if __name__ == "__main__":
    consulta_DBS("2025-11-28", "2025-12-01")