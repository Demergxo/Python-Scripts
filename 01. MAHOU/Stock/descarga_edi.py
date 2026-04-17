import os
import re
from urllib.parse import quote
import base64

import pandas as pd
import requests
#import openpyxl
from sqlalchemy import create_engine, text
from datetime import datetime

RAW_DIR = "raw_files"

def leer_excel(ruta_archivo, hoja=0):
    """
    Lee un archivo Excel y devuelve un DataFrame.
    """
    try:
        #leemos solo la columna A
        df = pd.read_excel(ruta_archivo, engine='openpyxl', sheet_name=hoja, usecols="A")
        
        #Eliminamos filas vacias y resetear índice
        df = df.dropna().reset_index(drop=True)
                
        return df
    except Exception as e:
        print(f"Error al leer el archivo {ruta_archivo}: {e}")
        return None 
    
def obtener_placeholders(lista, prefijo="id"):
    """
    Genera una lista de placeholders para una consulta SQL.
    """
    placeholders = ",".join([f":{prefijo}{i}" for i in range(len(lista))])
    params = {f"{prefijo}{i}": v for i, v in enumerate(lista)}
    
    return placeholders, params

def generar_nombres_unicos(filepath):
    base, ext = os.path.splitext(filepath)
    contador = 1

    while os.path.exists(filepath):
        filepath = f"{base}_{contador}{ext}"
        contador += 1
    return filepath

def generar_df_trabajo():

    engine = create_engine("mssql+pyodbc://@XGA_PROD")
    #Leer archivo excel
   
    df = leer_excel(r"C:\Users\jgmeras\OneDrive - GXO\Escritorio\Archivo_Subida_albaranes.xlsx", 1)

    if df is None or df.empty:
        print("El archivo está vacío o no se pudo leer.")
        return pd.DataFrame()  # Devuelve un DataFrame vacío en caso de error

    #Extraer valores únicos de la columna A
    valores = df.iloc[:, 0].dropna().astype(str).unique().tolist() #type:ignore
    
    if not valores:
        return pd.DataFrame()  # evita query inválida tipo IN ()

    placeholders, params = obtener_placeholders(valores)

    query_iddoc = text(f"""
        SELECT
            AlbaranDoc,
            ID_Doc AS [ID_Doc]
        FROM
            vDocumentos
        WHERE
            ID_Cliente = 944
            AND ID_Almacen = 129
            AND CodigoTipoDocumento = 'ALB'
            AND AlbaranDoc IN ({placeholders})
    """)

    with engine.connect() as conn:
        df_2 = pd.read_sql(query_iddoc, conn, params=params)
    print(df_2)

    if df_2.empty:
        print("No se encontraron registros.")
        return pd.DataFrame()
    
    # Extraer los ID_Doc como lista
    ids_alb = (
    df_2["ID_Doc"]
    .dropna()
    .astype(str)
    .str.strip()
    .loc[lambda x: x != ""]
    .unique()
    .tolist()
    )
    print(ids_alb)

    placeholders, params = obtener_placeholders(ids_alb)

    query_subestados = text(f"""
        SELECT
            ID_Doc AS [ID_Doc],
            ID_SubEstadosDocumentos AS [ID_SubEstadosDocumentos]
        FROM
            SubEstadosDocumentos
        WHERE
            ID_Cliente = 944
            AND ID_Doc IN ({placeholders})
    """)
    
    with engine.connect() as conn:
        df_3 = pd.read_sql(query_subestados, conn, params=params)
    print(df_3)

    df_23 = df_2.merge(df_3, on="ID_Doc", how="inner")

    id_subest =df_23["ID_SubEstadosDocumentos"].dropna().astype(str).unique().tolist()
    print(id_subest)

    placeholders, params = obtener_placeholders(id_subest)

    query_ficheros = text(f"""
        SELECT
            ID_SubEstadosDocumentos AS [ID_SubEstadosDocumentos],
            NombreFicheroBackupSubEstadoTransmision
        FROM
            SubEstadosTransmision
        WHERE
            ID_SubEstadosDocumentos IN ({placeholders})
    """)
    
    with engine.connect() as conn:
        df_4 = pd.read_sql(query_ficheros, conn, params=params)
    print(df_4)

    df_234 =df_23.merge(df_4, on="ID_SubEstadosDocumentos", how="inner")
    print(df_234)
    df_234.to_csv("prueba.csv", index=False, sep=";", encoding="utf-8")
    rutas =df_234["NombreFicheroBackupSubEstadoTransmision"].dropna().astype(str).unique().tolist()
    return rutas

def extraer_nombre_fichero(ruta, content_disposition='"'):
    if "filename=" in content_disposition:
        raw_filename = content_disposition.split("filename=")[-1].strip().strip('"')
        return os.path.basename(raw_filename).replace("\\", "_")
    
    nombre = os.path.basename(ruta.replace("\\", "/"))
    if nombre:
        return nombre
    
    m = re.search(r"I1084[^\\]+$", ruta)
    return m.group(0) if m else "fichero_descagado.edi"

def descargar_edi():
    user = "JGMERAS"
    password = "M1j3kMICrdmxlRFVY0g1"

    base_url = "http://10.19.16.125"
    download_path = "/fga/MtoDocumentosTr/DescargaFicheroSubestado"
    os.makedirs(RAW_DIR, exist_ok=True)
    ruta_list = generar_df_trabajo()
    if not ruta_list: #type:ignore
        print("No hay rutas para procesar.")
        return
    
    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0"
    })

    try:
        #hacemos login con la primera opción
        primera_ruta = ruta_list[0]
        primera_url = f"{base_url}{download_path}?ruta={quote(primera_ruta)}"#type:ignore

        r1 = session.get(primera_url, allow_redirects=True, timeout=30)

        login_url = r1.url
        payload = {
            "Nombre" : user,
            "password": password,
            "ActualizarPassword": "False",
            "Agenda": "False",
            "Error": "",
            "Login": "Aceptar",
        }
        headers = {
            "Referer": r1.url,
            "Content-Type": "application/x-www-form-urlencoded",
            "User-Agent": "Mozilla/5.0"
        }

        r2 = session.post(login_url, data=payload, headers=headers, allow_redirects=True, timeout=30)

        for ruta in ruta_list:
            try:
                ruta_codificada = quote(ruta) #type:ignore
                url = f"{base_url}{download_path}?ruta={ruta_codificada}"

                r3 = session.get(url, stream=True, timeout=60)
                print("Descarga: ",r3.status_code, url)
                content_type = (r3.headers.get("Content-Type") or "").lower()
                content_disposition = r3.headers.get("Content_Disposition", '"')

                if r3.status_code == 200:
                    filename = extraer_nombre_fichero(ruta, content_disposition)
                    print("Guardando como: ",filename)
                    
                    filepath = os.path.join(RAW_DIR, filename)
                    filepath = generar_nombres_unicos(filepath)

                    with open(filepath, "wb") as f:
                        for chunk in r3.iter_content(chunk_size=8192):
                            if chunk:
                                f.write(chunk)
                    print("Archivo guardado")
                else:
                    with open("error_response.html", "w", encoding="utf-8") as f:
                            f.write(r3.text)

                            print("Descarga erronea, se obtuvo HTML en vez del archivo")
            except Exception as e:
                print(f"Error descargando {ruta}: {e}")
    finally:
        session.close()

def extract_base64(lines):
    """
    Encuentra dónde empieza el contenido base64.
    Primero busca 'Content-Disposition:'.
    Si no lo encuentra, empieza desde la línea 5.
    """
    start_index = None

    for i, line in enumerate(lines):
        if "Content-Disposition:" in line:
            start_index = i + 1
            break

    if start_index is None:
        start_index = 5

    base64_data = "".join(lines[start_index:]).strip()
    return base64_data

def decode_file(filepath):
    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
        lines = f.readlines()

    base64_data = extract_base64(lines)

    try:
        decoded = base64.b64decode(base64_data)
        return decoded
    except Exception as e:
        print(f"Error decodificando {filepath}: \n{e}")
        return None

def extract_segments(edi_text):
    """
    Busca los segmentos requeridos dentro del EDI
    """
    results = {}

    patterns = {
        "BGM+80E Nº Pedido":r"BGM\+80E:[^+]*\+([^+]+)",
        "DTM+264 FCP Mayor o igual": r"DTM\+264:(\d{8})",
        "DTM+267 FCP exactamente igual": r"DTM\+267:(\d{8})",
        "RFF+FCP FCP según porcentaje vida útil": r"RFF\+FCP:([^']+)"
    }

    for key, pattern in patterns.items():
        match = re.search(pattern, edi_text)
        if match:
            result = match.group(1)

            if "DTM" in key:
                result = datetime.strptime(result, "%Y%m%d").strftime("%Y-%m-%d")

        else:
            result = None
        results[key] = result
    return results


def process_files(input_folder, output_folder):

    for filename in os.listdir(input_folder):

        filepath = os.path.join(input_folder, filename)

        if not os.path.isfile(filepath):
            continue

        print(f"Procesando: {filename}")

        decoded = decode_file(filepath)

        if decoded is None:
            continue

        edi_text = decoded.decode("utf-8", errors="ignore")

        # Guardar EDI
        edi_name = os.path.splitext(filename)[0] + ".edi"
        edi_path = os.path.join(output_folder, edi_name)

        with open(edi_path, "w", encoding="utf-8") as f:
            f.write(edi_text)

        # Extraer segmentos
        segments = extract_segments(edi_text)

        print("Segmentos encontrados:")
        for k, v in segments.items():
            print(f"  {k}: {v}")

        print("-" * 40)

if __name__ == "__main__":
    descargar_edi()
    process_files(RAW_DIR, "parsed_edis")
    