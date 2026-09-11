import os
import re
import json
import base64
import requests
import pandas as pd
from sqlalchemy import create_engine, text  # type: ignore
from datetime import datetime


# -----------------------------------------------------------------------------
# CONFIGURACIÓN
# -----------------------------------------------------------------------------
DATE = datetime.now().strftime("%Y%m%d%H%M%S")
DDBB_NAME = "KPIS_inb_out_steel"
FECHA_INICIO = "2026-06-01"
FECHA_FIN = "2026-08-31"
ALMACEN = 221
CLIENTE = 944

# Datos usados por el mismo servicio de descarga de descarga_edi_steel.py
USER_FGA = "JGMERAS"
PASSWORD_FGA = "M1j3kMICrdmxlRFVY0g1"
BASE_URL = "http://10.19.16.125"
DOWNLOAD_PATH = "/fga/MtoDocumentosTr/DescargaFicheroSubestado"


def hora():
    return datetime.now().strftime("%H:%M:%S")


def feedback(mensaje):
    print(f"[{hora()}] {mensaje}", flush=True)


def normalizar_pedido(valor):
    if pd.isna(valor):
        return ""
    return str(valor).strip().upper()


# -----------------------------------------------------------------------------
# OF / T11 -> LOCALIZAR JSON EN SUBESTADOS
# -----------------------------------------------------------------------------
def obtener_rutas_especiales_por_pedido(engine, pedidos, almacen=ALMACEN):
    """
    Devuelve un DataFrame con:
        Pedido | Ruta

    Solo conserva ficheros cuyo nombre empieza por OF o T11.
    """
    pedidos = [normalizar_pedido(p) for p in pedidos]
    pedidos = [p for p in pedidos if p.startswith(("OF", "T11"))]
    pedidos = list(dict.fromkeys(pedidos))

    if not pedidos:
        return pd.DataFrame(columns=["Pedido", "Ruta"])

    feedback(f"Buscando ficheros asociados a {len(pedidos)} pedido(s) OF/T11...")

    resultados = []
    chunk_size = 1500

    with engine.connect() as conn:
        total_bloques = (len(pedidos) + chunk_size - 1) // chunk_size
        for num_bloque, inicio in enumerate(range(0, len(pedidos), chunk_size), start=1):
            bloque = pedidos[inicio:inicio + chunk_size]
            feedback(f"Consulta de rutas OF/T11: bloque {num_bloque}/{total_bloques} ({len(bloque)} pedidos)")
            placeholders = ",".join(f":pedido{i}" for i in range(len(bloque)))
            params = {f"pedido{i}": pedido for i, pedido in enumerate(bloque)}
            params["almacen"] = almacen #type: ignore

            query = text(f"""
                SELECT DISTINCT
                    d.AlbaranDoc AS Pedido,
                    st.NombreFicheroBackupSubEstadoTransmision AS Ruta
                FROM vDocumentos d
                INNER JOIN SubEstadosDocumentos sd
                    ON sd.ID_Doc = d.ID_Doc
                   AND sd.ID_Cliente = d.ID_Cliente
                INNER JOIN SubEstadosTransmision st
                    ON st.ID_SubEstadosDocumentos = sd.ID_SubEstadosDocumentos
                WHERE d.ID_Cliente = {CLIENTE}
                  AND d.ID_Almacen = :almacen
                  AND d.AlbaranDoc IN ({placeholders})
                  AND st.NombreFicheroBackupSubEstadoTransmision IS NOT NULL
            """)

            resultados.append(pd.read_sql(query, conn, params=params))

    if not resultados:
        return pd.DataFrame(columns=["Pedido", "Ruta"])

    df_rutas = pd.concat(resultados, ignore_index=True)

    if df_rutas.empty:
        return pd.DataFrame(columns=["Pedido", "Ruta"])

    df_rutas["Pedido"] = df_rutas["Pedido"].map(normalizar_pedido)
    df_rutas["Ruta"] = df_rutas["Ruta"].astype(str).str.strip()

    # El fichero JSON que nos interesa empieza por OF o T11.
    mask_especial = df_rutas["Ruta"].map(
        lambda ruta: os.path.basename(ruta.replace("\\", "/")).upper().startswith(("OF", "T11"))
    )

    df_resultado = df_rutas.loc[mask_especial, ["Pedido", "Ruta"]].drop_duplicates()
    feedback(f"Ficheros OF/T11 localizados: {len(df_resultado)}")
    return df_resultado


# -----------------------------------------------------------------------------
# LECTURA DEL JSON OF / T11
# -----------------------------------------------------------------------------
def leer_json_respuesta(raw_bytes):
    """
    Intenta interpretar la respuesta como JSON directo.
    Como respaldo admite JSON envuelto en texto/MIME o codificado en base64.
    """
    try:
        return json.loads(raw_bytes.decode("utf-8-sig"))
    except Exception:
        pass

    texto = raw_bytes.decode("utf-8", errors="ignore")

    # JSON incrustado dentro de texto.
    for apertura, cierre in (("[", "]"), ("{", "}")):
        inicio = texto.find(apertura)
        fin = texto.rfind(cierre)
        if inicio != -1 and fin > inicio:
            try:
                return json.loads(texto[inicio:fin + 1])
            except Exception:
                pass

    # Respuesta MIME/base64.
    lineas = texto.splitlines()
    candidatos = []
    en_cuerpo = False

    for linea in lineas:
        limpia = linea.strip()

        if not en_cuerpo:
            if limpia == "":
                en_cuerpo = True
            continue

        if limpia.startswith("--"):
            break

        if re.fullmatch(r"[A-Za-z0-9+/=]+", limpia):
            candidatos.append(limpia)

    if candidatos:
        try:
            decodificado = base64.b64decode("".join(candidatos), validate=True)
            return json.loads(decodificado.decode("utf-8-sig"))
        except Exception:
            pass

    return None


def extraer_sscc_json(data_json):
    """
    Extrae los SSCC reales de los formatos OF y T11 de RegistroProcesado.

    Formatos esperados:

    - OF...  -> SSCC01 y SSCC02
    - T11... -> SSCC

    Ejemplo OF:
    [
        {
            "FechaProceso": "...",
            "RegistroProcesado": "{\\"SSCC01\\":\\"...\\",\\"SSCC02\\":\\"...\\", ...}"
        }
    ]

    RegistroProcesado es un JSON serializado como texto, por lo que se hace
    un segundo json.loads(). Los SSCC vacíos se ignoran y los repetidos se
    eliminan mediante set(). En T11 se ignora deliberadamente SSCC_TRUNCADO.
    """
    sscc_unicos = set()

    if not isinstance(data_json, list):
        return sscc_unicos

    for registro in data_json:
        if not isinstance(registro, dict):
            continue

        registro_procesado = registro.get("RegistroProcesado")
        if not registro_procesado:
            continue

        # Normalmente viene como string, pero dejamos soporte por si algún día
        # el origen empieza a devolverlo ya convertido en objeto.
        if isinstance(registro_procesado, str):
            try:
                detalle = json.loads(registro_procesado)
            except (json.JSONDecodeError, TypeError):
                continue
        elif isinstance(registro_procesado, dict):
            detalle = registro_procesado
        else:
            continue

        for campo in ("SSCC01", "SSCC02", "SSCC"):
            valor = detalle.get(campo)

            if valor is None:
                continue

            sscc = str(valor).strip()
            if sscc:
                sscc_unicos.add(sscc)

    return sscc_unicos


# -----------------------------------------------------------------------------
# DESCARGA DE LOS JSON OF/T11 + RECUENTO SSCC
# -----------------------------------------------------------------------------
def obtener_sscc_unicos_por_pedidos(engine, pedidos, almacen=ALMACEN):
    """
    Devuelve un diccionario:
        {"OF2615403": 32, "T11...": 18, ...}

    Si no encuentra fichero o no puede procesarlo, ese pedido queda a 0.
    Si existen varios ficheros OF/T11 para un mismo pedido, une todos sus SSCC
    antes de contar, evitando duplicados entre ficheros.
    """
    pedidos = [normalizar_pedido(p) for p in pedidos]
    pedidos = [p for p in pedidos if p.startswith(("OF", "T11"))]
    pedidos = list(dict.fromkeys(pedidos))

    resultado = {pedido: 0 for pedido in pedidos}

    if not pedidos:
        return resultado

    df_rutas = obtener_rutas_especiales_por_pedido(engine, pedidos, almacen)

    if df_rutas.empty:
        print("⚠️ No se encontraron ficheros OF/T11 para los pedidos indicados.")
        return resultado

    session = requests.Session()
    session.headers.update({"User-Agent": "Mozilla/5.0"})

    try:
        feedback("Conectando con el servicio de descarga FGA...")
        # Primera petición para obtener la URL real del formulario de login.
        primera_ruta = df_rutas.iloc[0]["Ruta"]
        r1 = session.get(
            f"{BASE_URL}{DOWNLOAD_PATH}",
            params={"nombrefichero": primera_ruta},
            allow_redirects=True,
            timeout=30,
        )

        payload = {
            "Nombre": USER_FGA,
            "password": PASSWORD_FGA,
            "ActualizarPassword": "False",
            "Agenda": "False",
            "Error": "",
            "Login": "Aceptar",
        }

        headers = {
            "Referer": r1.url,
            "Content-Type": "application/x-www-form-urlencoded",
            "User-Agent": "Mozilla/5.0",
        }

        session.post(
            r1.url,
            data=payload,
            headers=headers,
            allow_redirects=True,
            timeout=30,
        )

        feedback("Autenticación completada. Comenzando descarga y análisis de JSON...")

        sscc_por_pedido = {pedido: set() for pedido in pedidos}
        total_ficheros = len(df_rutas)

        for num_fichero, (_, fila) in enumerate(df_rutas.iterrows(), start=1):
            pedido = normalizar_pedido(fila["Pedido"])
            ruta = str(fila["Ruta"]).strip()
            nombre_fichero = os.path.basename(ruta.replace("\\", "/"))

            try:
                feedback(f"[{num_fichero}/{total_ficheros}] Descargando {nombre_fichero} para {pedido}...")
                respuesta = session.get(
                    f"{BASE_URL}{DOWNLOAD_PATH}",
                    params={"nombrefichero": ruta},
                    timeout=60,
                )

                if respuesta.status_code != 200:
                    print(f"⚠️ {pedido}: descarga HTTP {respuesta.status_code}")
                    continue

                data_json = leer_json_respuesta(respuesta.content)

                if data_json is None:
                    print(f"⚠️ {pedido}: {nombre_fichero} no se pudo interpretar como JSON")
                    continue

                encontrados = extraer_sscc_json(data_json)
                sscc_por_pedido.setdefault(pedido, set()).update(encontrados)

                feedback(
                    f"{pedido}: {len(encontrados)} SSCC únicos en {nombre_fichero}"
                )

            except Exception as e:
                print(
                    f"⚠️ {pedido}: error procesando {nombre_fichero}: "
                    f"{type(e).__name__}: {e}"
                )

        for pedido, valores in sscc_por_pedido.items():
            resultado[pedido] = len(valores)

        feedback("Recuento de SSCC completado para los pedidos OF/T11.")

    finally:
        session.close()

    return resultado


# -----------------------------------------------------------------------------
# CONSULTA PRINCIPAL
# -----------------------------------------------------------------------------
def qry_inb_out(fecha_inicio, fecha_fin):
    feedback(f"Inicio del proceso. Rango: {fecha_inicio} -> {fecha_fin}")
    feedback("Conectando con SQL Server...")

    engine = create_engine("mssql+pyodbc://@XGA_PROD")

    try:
        query_docs = text("""
            SELECT
                ID_Doc,
                NombreTipoDocumento AS 'Movimiento',
                FechaProcesoDoc AS 'Fecha',
                AlbaranDoc AS 'Documento',
                PaletsClienteDoc AS 'Palets',
                PesoFiege AS 'Peso',
                ObsEstado AS 'Observaciones'
            FROM vDocumentos
            WHERE
                ID_Cliente = 944
                AND ID_Almacen = 221
                AND (CodigoTipoDocumento = 'RS' OR CodigoTipoDocumento = 'ALB')
                AND CodigoTipoEstado IN ('040', '080', '085', '140', '130')
                AND CONVERT(date, FechaDoc)
                    BETWEEN CONVERT(date, :inicio) AND CONVERT(date, :fin);
        """)

        feedback("Ejecutando consulta principal de movimientos...")
        with engine.connect() as conn:
            df_doc = pd.read_sql(
                query_docs,
                conn,
                params={"inicio": fecha_inicio, "fin": fecha_fin},
            )

        feedback(f"Consulta principal terminada: {len(df_doc)} filas recuperadas.")

        # Normalizamos columnas clave.
        df_doc["Movimiento"] = df_doc["Movimiento"].fillna("").str.strip().str.upper()
        df_doc["Documento"] = df_doc["Documento"].fillna("").astype(str).str.strip()
        df_doc["Palets"] = pd.to_numeric(df_doc["Palets"], errors="coerce")
        df_doc["Peso"] = pd.to_numeric(df_doc["Peso"], errors="coerce")

        # Eliminamos movimientos con peso negativo.
        filas_antes = len(df_doc)
        df_doc = df_doc.loc[df_doc["Peso"].isna() | (df_doc["Peso"] >= 0)].copy()
        eliminadas = filas_antes - len(df_doc)
        feedback(f"Filtro de peso aplicado: {eliminadas} fila(s) con peso negativo eliminadas.")

        # ID_Doc de los ALBARANES para calcular palets teóricos.
        ids_alb = (
            df_doc.loc[df_doc["Movimiento"] == "ALBARAN", "ID_Doc"]
            .dropna()
            .astype(int)
            .unique()
            .tolist()
        )

        if "Fecha" in df_doc.columns:
            df_doc["Fecha"] = (
                pd.to_datetime(df_doc["Fecha"], errors="coerce")
                .dt.strftime("%d/%m/%Y")
                .fillna("")
            )

        # ------------------------------------------------------------------
        # PALETS TEÓRICOS
        # ------------------------------------------------------------------
        dfs_palets = []
        chunk_size = 2000

        if ids_alb:
            feedback(f"Calculando palets teóricos para {len(ids_alb)} albarán(es)...")
            with engine.connect() as conn:
                total_bloques = (len(ids_alb) + chunk_size - 1) // chunk_size
                for num_bloque, inicio in enumerate(range(0, len(ids_alb), chunk_size), start=1):
                    feedback(f"Palets teóricos: bloque {num_bloque}/{total_bloques}")
                    ids_chunk = ids_alb[inicio:inicio + chunk_size]
                    placeholders = ", ".join(
                        f":id{i}" for i in range(len(ids_chunk))
                    )

                    query_palets = text(f"""
                        SELECT
                            ID_Doc,
                            CEILING(TotalPalets) AS Palets_Teoricos
                        FROM vDocumentosPaletsTeoricos
                        WHERE
                            ID_Cliente = 944
                            AND ID_Doc IN ({placeholders})
                    """)

                    params = {
                        f"id{i}": valor
                        for i, valor in enumerate(ids_chunk)
                    }

                    dfs_palets.append(
                        pd.read_sql(query_palets, conn, params=params)
                    )

        if dfs_palets:
            df_palets = pd.concat(dfs_palets, ignore_index=True)
        else:
            df_palets = pd.DataFrame(columns=["ID_Doc", "Palets_Teoricos"])

        df = df_doc.merge(df_palets, on="ID_Doc", how="left")
        feedback("Cálculo de palets teóricos terminado.")

        # Solo para ALBARAN, sustituimos Palets por el cálculo teórico.
        mask = (
            (df["Movimiento"] == "ALBARAN")
            & df["Palets_Teoricos"].notna()
        )
        df.loc[mask, "Palets"] = df.loc[mask, "Palets_Teoricos"]

        # ------------------------------------------------------------------
        # PEDIDOS OF/T11 -> JSON -> SSCC ÚNICOS
        # ------------------------------------------------------------------
        documentos_normalizados = df["Documento"].map(normalizar_pedido)
        mask_especial = documentos_normalizados.str.startswith(("OF", "T11"))

        documentos_especiales = (
            documentos_normalizados.loc[mask_especial]
            .drop_duplicates()
            .tolist()
        )

        if documentos_especiales:
            n_of = sum(p.startswith("OF") for p in documentos_especiales)
            n_t11 = sum(p.startswith("T11") for p in documentos_especiales)
            feedback(
                f"Pedidos especiales encontrados: {len(documentos_especiales)} "
                f"(OF: {n_of}, T11: {n_t11})"
            )

            sscc_por_pedido = obtener_sscc_unicos_por_pedidos(
                engine,
                documentos_especiales,
                almacen=ALMACEN,
            )

            # Para pedidos OF/T11 el número real de palets se obtiene contando
            # los SSCC únicos del JSON, ya que no existe en las tablas.
            df.loc[mask_especial, "Palets"] = (
                documentos_normalizados.loc[mask_especial]
                .map(sscc_por_pedido)
                .fillna(0)
                .astype("Int64")
            )
            feedback("Palets de pedidos OF/T11 actualizados con el número de SSCC únicos.")
        else:
            feedback("No se han encontrado pedidos OF/T11 en el rango consultado.")

        # Limpieza final.
        df.drop(columns=["Palets_Teoricos", "ID_Doc"], inplace=True)
        df["Palets"] = df["Palets"].astype("Int64")

        nombre_archivo = f"{DDBB_NAME}_{DATE}.xlsx"
        feedback(f"Generando Excel final ({len(df)} filas): {nombre_archivo}")
        df.to_excel(nombre_archivo, index=False)

        feedback(f"✅ Archivo generado correctamente: {nombre_archivo}")
        feedback("Proceso finalizado.")

    finally:
        engine.dispose()


if __name__ == "__main__":
    qry_inb_out(FECHA_INICIO, FECHA_FIN)
