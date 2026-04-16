import os
import requests
from urllib.parse import quote
import pandas as pd
import openpyxl
from sqlalchemy import create_engine, text
import re

def leer_excel(ruta_archivo, hoja=0):
    """
    Lee un archivo Excel y devuelve un DataFrame.
    """
    try:
        #leemos solo la columna A
        df = pd.read_excel(ruta_archivo, engine='openpyxl', sheet_name=hoja, usecols="A")
        
        #Eliminamos filas vacias
        df = df.dropna()
        #Resetear índice
        df = df.reset_index(drop=True)
        
        return df
    except Exception as e:
        print(f"Error al leer el archivo {ruta_archivo}: {e}")
        return None 

def generar_df_trabajo():

    engine = create_engine("mssql+pyodbc://@XGA_PROD")
    #Leer archivo excel
    df = leer_excel(r"Z:\Shared\Logistica\01. MAHOU\Stock\Listado de pedidos Mahou.xlsx", 1)

    #Extraer valores únicos de la columna A
    valores = df.iloc[:, 0].dropna().astype(str).unique().tolist() #type:ignore

    if not valores:
        return pd.DataFrame()  # evita query inválida tipo IN ()

    placeholders = ", ".join([f":id{i}" for i in range(len(valores))])

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
    params = {f"id{i}": v for i, v in enumerate(valores)}
    
    with engine.connect() as conn:
        df_2 = pd.read_sql(query_iddoc, conn, params=params)
    print(df_2)
    
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

    placeholders = ", ".join([f":id{i}" for i in range(len(ids_alb))])

    query_subestados = text(f"""
        SELECT
            ID_Doc AS [ID_Doc]
            ID_SubEstadosDocumentos AS [ID_SubEstadosDocumentos]
        FROM
            SubEstadosDocumentos
        WHERE
            ID_Cliente = 944
            AND ID_Doc IN ({placeholders})
    """)
    params = {f"id{i}": v for i, v in enumerate(ids_alb)}

    with engine.connect() as conn:
        df_3 = pd.read_sql(query_subestados, conn, params=params)
    print(df_3)

    df_23 = df_2.merge(df_3, on="ID_Doc", how="inner")

    id_subest =df_23["ID_SubEstadosDocumentos"].dropna().astype(str).unique().tolist()
    print(id_subest)

    placeholders = ", ".join([f":id{i}" for i in range(len(id_subest))])

    query_ficheros = text(f"""
        SELECT
            ID_SubEstadosDocumentos AS [ID_SubEstadosDocumentos]
            NombreFicheroBackupSubEstadoTransmision
        FROM
            SubEstadosTransmision
        WHERE
            ID_SubEstadosDocumentos IN ({placeholders})
    """)
    params = {f"id{i}": v for i, v in enumerate(id_subest)}
    with engine.connect() as conn:
        df_4 = pd.read_sql(query_ficheros, conn, params=params)
    print(df_4)

    df_234 =df_23.merge(df_4, on="ID_SubEstadosDocumentos", how="inner")
    print(df_234)
    df_234.to_csv("prueba.csv", index=False, sep=";", encoding="utf-8")
    id_resul =df_234["NombreFicheroBackupSubEstadoTransmision"].dropna().astype(str).unique().tolist()
    return id_resul

def descargar_edi():
    user = "JGMERAS"
    password = "M1j3kMICrdmxlRFVY0g1"

    base_url = "http://10.19.16.125"
    download_path = "/fga/MtoDocumentosTr/DescargaFicheroSubestado"
    ruta_list = generar_df_trabajo()

    for ruta in ruta_list:

        # Codificar correctamente
        ruta_codificada = quote(ruta)

        url = f"{base_url}{download_path}?nombrefichero={ruta_codificada}"

        session = requests.Session()
        session.headers.update({"User-Agent":"Mozilla/5.0",})

        # 1. Entrar en la URL preotegida para que el servidor nos redirija al login
        r1 = session.get(url, allow_redirects=True, timeout=30)
        print("Paso 1:",r1.status_code, r1.url)

        # 2. Construir la URL de login
        login_url = r1.url

        payload = {
            "Nombre": user,
            "password": password,
            "ActualizarPassword": "False",
            "Agenda": "False",
            "Error": "",
            "Login": "Aceptar",
        }

        headers = {
            "Refer": r1.url,
            "Content-Type": "application/x-www-form-urlencoded",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        }

        # 3. Enviar login
        r2 = session.post(login_url, data=payload, headers=headers, allow_redirects=True, timeout=30)
        print("Paso 2:", r2.status_code, r2.url)

        # 4. Intentar la descarga con la sesión autorizada
        r3 = session.get(url, stream=True, timeout=60)
        print("Paso 3:", r3.status_code)
        print("Content-Type:", r3.headers.get("Content-Type"))
        print("Content-Disposition:", r3.headers.get("Content-Disposition"))

        # 5. Comprobar si sigue devolviendo html
        content_type = (r3.headers.get("Content-Type") or "").lower()


        if r3.status_code == 200 and "text/html" not in content_type:
            filename = str(re.search(r'I1084[^\\]+$', ruta_codificada))

            #probar capturar el nombre que manda el server
            content_disposition = r3.headers.get("Content-Disposition", "")
            if "filename" in content_disposition:
                raw_filename = content_disposition.split("filename=")[-1].strip().strip('"')

                filename = os.path.basename(raw_filename)
                filename = filename.replace("\\","_")
            print("Intentando guardar como:", filename)
            
            with open(filename, "wb") as f:
                    for chunk in r3.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
            
            
            print(f"Archivo guardado como {filename}")
        else:
            #Guardamos la respuesta
            with open("error_response.html", "w", encoding="utf-8") as f:
                f.write(r3.text)
                print("Se ha guardado la respuesta HTML de error en 'error_response.html'")
            
            print("La descarga falló. Se obtuvo una respuesta HTML de error." )
            print("Se ha guardado la respuesta en 'error_response.html'")
                
            
