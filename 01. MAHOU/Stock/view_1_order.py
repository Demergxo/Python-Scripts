import os
import re

import base64
from alive_progress import alive_bar

import pandas as pd
import requests
#import openpyxl
from sqlalchemy import create_engine, text
from datetime import datetime

from pyfiglet import Figlet
from tabulate import tabulate
from colorama import Fore, Style, init

init(autoreset=True)

base_path = os.path.dirname(os.path.abspath(__file__))
almacen = 221

RAW_DIR = os.path.join(base_path, "raw_files")

def view_order(dataframe, pedido):

    if dataframe is None or dataframe.empty:
        print(Fore.RED + "\nNo hay información EDI para mostrar.")
        return

    pedido_buscado = str(pedido).strip()

    df_pedido = dataframe[
        dataframe["Pedido"].astype(str).str.strip() == pedido_buscado
    ].copy()

    if df_pedido.empty:
        print(Fore.RED + f"\nNo se encontró el pedido {pedido_buscado}.")
        return

    tabla = []

    for _, fila in df_pedido.iterrows():

        referencia = fila["Referencia"]

        if pd.isna(referencia) or str(referencia).strip() == "":
            referencia = "SIN REFERENCIA"

        tabla.append([
            fila["Línea"],
            referencia,
            fila["Tipo FCP"],
            fila.get("Valor FCP", "")
        ])

    figlet = Figlet(font="slant")

    print(Fore.CYAN)
    print(figlet.renderText("FCP PEDIDO"))

    print(
        Fore.WHITE
        + Style.BRIGHT
        + f"Pedido: {pedido_buscado}\n"
    )

    print(
        Fore.CYAN
        + tabulate(
            tabla,
            headers=["Línea", "Referencia", "Tipo FCP", "Valor"],
            tablefmt="fancy_grid",
            stralign="left",
            numalign="center"
        )
    )

    print(
        Fore.GREEN
        + Style.BRIGHT
        + f"\nTotal de líneas: {len(tabla)}"
    )

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
    
def obtener_placeholders(lista, almacen, prefijo="id" ): #type: ignore
    """
    Genera una lista de placeholders para una consulta SQL.
    """
    placeholders = ",".join([f":{prefijo}{i}" for i in range(len(lista))])
    params = {f"{prefijo}{i}": v for i, v in enumerate(lista)}
    params["almacen"] = almacen
    
    return placeholders, params

def generar_nombres_unicos(filepath):
    base, ext = os.path.splitext(filepath)
    contador = 1

    while os.path.exists(filepath):
        filepath = f"{base}_{contador}{ext}"
        contador += 1
    return filepath

def generar_df_trabajo(df, almacen):

    engine = create_engine("mssql+pyodbc://@XGA_PROD")
    #Leer archivo excel
 
    if df is None or df.empty:
        print("El archivo está vacío o no se pudo leer.")
        return pd.DataFrame()  # Devuelve un DataFrame vacío en caso de error

    #Extraer valores únicos de la columna A
    valores = df.iloc[:, 0].dropna().astype(str).unique().tolist() #type:ignore
    
    if not valores:
        return pd.DataFrame()  # evita query inválida tipo IN ()

    placeholders, params = obtener_placeholders(valores, almacen=almacen)

    query_iddoc = text(f"""
        SELECT
            AlbaranDoc,
            ID_Doc AS [ID_Doc]
        FROM
            vDocumentos
        WHERE
            ID_Cliente = 944
            AND ID_Almacen = :almacen
            AND CodigoTipoDocumento = 'ALB'
            AND AlbaranDoc IN ({placeholders})
    """)

    with engine.connect() as conn:
        df_2 = pd.read_sql(query_iddoc, conn, params=params)
    #print(df_2)

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
    #print(ids_alb)

    placeholders, params = obtener_placeholders(ids_alb, almacen=almacen)

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
    #print(df_3)

    df_23 = df_2.merge(df_3, on="ID_Doc", how="inner")

    id_subest =df_23["ID_SubEstadosDocumentos"].dropna().astype(str).unique().tolist()
    #print(id_subest)

    placeholders, params = obtener_placeholders(id_subest, almacen=almacen)

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
    #print(df_4)

    df_234 =df_23.merge(df_4, on="ID_SubEstadosDocumentos", how="inner")
    #print(df_234)
    #df_234.to_csv("prueba1.csv", index=False, sep=";", encoding="utf-8")
    rutas =df_234["NombreFicheroBackupSubEstadoTransmision"].dropna().astype(str).unique().tolist()
    return rutas

def extraer_nombre_fichero(ruta, content_disposition=''):

    # 1. Intentar desde header
    if "filename=" in content_disposition:
        raw_filename = content_disposition.split("filename=")[-1].strip().strip('"')
        nombre = os.path.basename(raw_filename)

    else:
        # 2. Sacar desde ruta
        nombre = os.path.basename(ruta.replace("\\", "/"))

    # 3. Validar que empiece por I1084
    if not nombre.startswith("I1084"):
        return None  # 👈 clave para filtrar

    # 4. Limpiar caracteres problemáticos
    nombre = nombre.replace("\\", "_")

    return nombre

def descargar_edi(df, almacen):
    limpiar_raw_files(RAW_DIR)
    user = "JGMERAS"
    password = "M1j3kMICrdmxlRFVY0g1"

    base_url = "http://10.19.16.125"
    download_path = "/fga/MtoDocumentosTr/DescargaFicheroSubestado"

    if not os.path.exists(RAW_DIR):
        print(f"Creando carpeta: {RAW_DIR}")
        os.makedirs(RAW_DIR, exist_ok=True)

    ruta_list = generar_df_trabajo(df, almacen)

    # Si no hay rutas para procesar
    if ruta_list is None:
        print("No hay rutas para procesar.")
        return pd.DataFrame()

    if isinstance(ruta_list, pd.DataFrame):
        if ruta_list.empty:
            print("No hay rutas para procesar.")
            return pd.DataFrame()
    else:
        if len(ruta_list) == 0:
            print("No hay rutas para procesar.")
            return pd.DataFrame()
    
    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0"
    })

    try:
        #hacemos login con la primera opción
        primera_ruta = ruta_list[0]
        primera_url = f"{base_url}{download_path}?nombrefichero={primera_ruta}"

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
                ruta_codificada = (ruta) #type:ignore
                url = f"{base_url}{download_path}?nombrefichero={ruta_codificada}"

                r3 = session.get(url, stream=True, timeout=60)
                #print("Descarga: ",r3.status_code, url)
                content_type = (r3.headers.get("Content-Type") or "").lower()
                content_disposition = r3.headers.get("Content-Disposition", "")

                if r3.status_code == 200:
                    filename = extraer_nombre_fichero(ruta, content_disposition)
                    # Si la ruta no corresponde a un I1084, la ignoramos
                    if not filename:
                        continue

                    filepath = os.path.join(RAW_DIR, filename)
                    filepath = generar_nombres_unicos(filepath)

                    with open(filepath, "wb") as f:
                        for chunk in r3.iter_content(chunk_size=8192):
                            if chunk:
                                f.write(chunk)
                    #print("Archivo guardado")
                else:
                    with open("error_response.html", "w", encoding="utf-8") as f:
                            f.write(r3.text)

                            #print("Descarga erronea, se obtuvo HTML en vez del archivo")
            except Exception as e:
                print(Fore.YELLOW + f"⚠️ Error descargando {ruta}: {type(e).__name__}: {e}")
                continue
                

    finally:
        session.close()

    # Una vez descargados los EDI, los procesamos y devolvemos el DataFrame
    return process_files(RAW_DIR)

def process_files(input_folder):
    filas = []

    files = [
        f for f in os.listdir(input_folder)
        if os.path.isfile(os.path.join(input_folder, f))
    ]

    total_files = len(files)

    with alive_bar(total_files, title="Procesando archivos") as bar:

        for filename in files:

            filepath = os.path.join(input_folder, filename)

            edi_text = decode_file(filepath)

            if edi_text is None:
                bar()
                continue

            data = extract_segments(edi_text)
            pedido = data["pedido"]

            for numero_linea, linea in enumerate(data["lineas"], start=1):

                filas.append({
                    "Pedido": pedido,
                    "Línea": numero_linea,
                    "Referencia": linea["referencia"],
                    "Tipo FCP": linea["tipo_fcp"],
                    "Valor FCP": linea["valor_fcp"],
                    "Archivo": filename
                })

            bar()

    return pd.DataFrame(filas)

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
    
    with open(filepath, "rb") as f:
        raw = f.read()

    # 1) intentar leer como texto directamente
    text = raw.decode("utf-8", errors="ignore")

    # Si ya parece EDI, no decodificamos
    if "UNB" in text or "UNH" in text or "LIN+" in text:
        return text

    # 2) si no, intentar decodificar base64
    lines = text.splitlines()

    candidate_lines = []
    in_body = False

    for line in lines:
        line_strip = line.strip()

        #Saltar cabeceras MIME hasta la primera línea vacía
        if not in_body:
            if line_strip == "":
                in_body = True
            continue

        # Cortamos si llega boundary final
        if line_strip.startswith("--"):
            break

        #Nos quedamos con base64
        if re.fullmatch(r"[A-Za-z0-9+/=]+", line_strip):
            candidate_lines.append(line_strip)
    
    base64_data = "".join(candidate_lines)

    if not base64_data:
        print("⚠️ No se encontró contenido base64 válido.")
        print(f"Ruta: {filepath}")
        print("Primeras 200 chars:", repr(text[:200]))
        return None

    try:
        decoded_bytes = base64.b64decode(base64_data, validate=True)
    except Exception as e:
        print("❌ Error decodificando base64:")
        print(f"Ruta: {filepath}")
        print(f"Error: {e}")
        print("Base64 data (primeros 200 chars):", repr(base64_data[:200]))
        return None
    
    edit_text = decoded_bytes.decode("utf-8", errors="ignore")

    if "LIN+" not in edit_text:
        print("⚠️ El texto decodificado no parece ser un archivo EDI válido.")
        print(f"Ruta: {filepath}")
        print("Primeras 200 chars:", repr(edit_text[:200]))
        return None
    
    return edit_text
    
def extract_segments(edi_text):
    result = {
        "pedido": None,
        "lineas": []
    }

    # Pedido (cabecera). Admite BGM+80E:...+PEDIDO y BGM+80E+PEDIDO
    match = re.search(r"BGM\+80E(?::[^+]*)?\+([^+']+)", edi_text)
    if match:
        result["pedido"] = match.group(1).strip()

    # Cada bloque LIN corresponde a una referencia/línea del pedido
    bloques = re.split(r"(?=LIN\+)", edi_text)

    for bloque in bloques:
        if not bloque.startswith("LIN+"):
            continue

        referencia = None
        tipo_fcp = "SIN FCP"
        valor_fcp = ""

        pia = re.search(r"PIA\+1\+([^:+']+):SA", bloque)
        if pia:
            referencia = pia.group(1).strip()

        # Mantenemos la misma lógica del script original, pero mostrando
        # también el valor asociado para que la consulta sea más útil.
        dtm264 = re.search(r"DTM\+264:(\d{8})", bloque)
        dtm267 = re.search(r"DTM\+267:(\d{8})", bloque)
        rff_fcp = re.search(r"RFF\+FCP:([^']+)", bloque)

        if dtm264:
            tipo_fcp = "FCP DESDE"
            valor_fcp = datetime.strptime(dtm264.group(1), "%Y%m%d").strftime("%d/%m/%Y")
        elif dtm267:
            tipo_fcp = "FCP EXACTA"
            valor_fcp = datetime.strptime(dtm267.group(1), "%Y%m%d").strftime("%d/%m/%Y")
        elif rff_fcp:
            tipo_fcp = "FCP POR PORCENTAJE"
            valor_fcp = rff_fcp.group(1).strip()

        result["lineas"].append({
            "referencia": referencia,
            "tipo_fcp": tipo_fcp,
            "valor_fcp": valor_fcp
        })

    return result

def limpiar_raw_files(folder_path):
    if not os.path.exists(folder_path):
        print(f"La carpeta no existe: {folder_path}")
        return

    archivos_eliminados = 0

    for filename in os.listdir(folder_path):
        filepath = os.path.join(folder_path, filename)

        if os.path.isfile(filepath):
            try:
                os.remove(filepath)
                archivos_eliminados += 1
            except Exception as e:
                print(f"Error eliminando {filename}: {e}")

    print(f"Archivos eliminados: {archivos_eliminados}")

def inspect_edi(pedido):

    pedido = str(pedido).strip()

    if not pedido:
        print(Fore.RED + "Debes indicar un número de pedido.")
        return

    # Crear un DataFrame igual que espera generar_df_trabajo()
    df = pd.DataFrame({"Pedido": [pedido]})

    resultados = descargar_edi(df, almacen)

    view_order(resultados, pedido)

if __name__ == "__main__":

    pedido = input("Introduce el número de pedido: ")

    inspect_edi(pedido)
    