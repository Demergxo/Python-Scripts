import os
import time
import pandas as pd
from sqlalchemy import create_engine, text
from xlsxwriter.utility import xl_col_to_name


path = os.getcwd()
DB_FILE = os.path.join(path, "apoyo.db")
USER = os.getenv("USERNAME")

almacen = 221

def buscar_stock_referencia_alternativa(df_stock_base, referencia, fecha_requerida):
    """
    Busca stock de una referencia alternativa.

    Si hay fecha requerida:
        busca Caducidad >= fecha_requerida.
    Si no hay fecha requerida:
        usa la caducidad más antigua disponible.

    No descuenta stock, solo informa fecha y stock disponible.
    """

    if referencia is None or str(referencia).strip() == "":
        return pd.NaT, 0

    referencia = str(referencia).strip()

    stock_ref = df_stock_base[
        (df_stock_base["Referencia"] == referencia)
        & (df_stock_base["Stock"] > 0)
    ].copy()

    if stock_ref.empty:
        return pd.NaT, 0

    if pd.notna(fecha_requerida):
        stock_ref = stock_ref[stock_ref["Caducidad"] >= fecha_requerida]

    if stock_ref.empty:
        return pd.NaT, 0

    stock_ref = stock_ref.sort_values("Caducidad")

    fecha_propuesta = stock_ref.iloc[0]["Caducidad"]
    stock_disponible = stock_ref["Stock"].sum()

    return fecha_propuesta, stock_disponible

def buscar_stock_referencia_inversa(df_stock_base, referencia, fecha_requerida):
    """
    Busca stock de una referencia alternativa/inversa.

    Si hay fecha requerida:
        busca caducidad >= fecha_requerida.
    Si no hay fecha requerida:
        busca la fecha más antigua disponible.

    No descuenta stock, solo informa.
    """

    if referencia is None or str(referencia).strip() == "":
        return pd.NaT, 0

    referencia = str(referencia).strip()

    stock_ref = df_stock_base[
        (df_stock_base["Referencia"] == referencia)
        & (df_stock_base["Stock"] > 0)
    ].copy()

    if stock_ref.empty:
        return pd.NaT, 0

    if pd.notna(fecha_requerida):
        stock_ref = stock_ref[stock_ref["Caducidad"] >= fecha_requerida]

    if stock_ref.empty:
        return pd.NaT, 0

    stock_ref = stock_ref.sort_values("Caducidad")

    fecha_propuesta = stock_ref.iloc[0]["Caducidad"]
    stock_disponible = stock_ref["Stock"].sum()

    return fecha_propuesta, stock_disponible


def marcar_fila_borde_rojo(worksheet, fila_excel, ultima_columna, formato_linea_borde_rojo):
    """
    Aplica borde rojo a toda una fila del Excel.
    fila_excel debe ser el índice real de fila en Excel/XlsxWriter.
    """
    worksheet.conditional_format(
        fila_excel,
        0,
        fila_excel,
        ultima_columna,
        {
            "type": "formula",
            "criteria": "=TRUE",
            "format": formato_linea_borde_rojo
        }
    )


def consumir_stock_sin_restriccion(stock_virtual, referencia, cantidad):
    """
    Consume stock de una referencia sin restricción de FCP.
    Usa la caducidad más antigua disponible.
    Si no hay stock suficiente para servir íntegramente, NO descuenta stock.
    """

    if cantidad <= 0:
        return pd.NaT, 0, ""

    candidatos = stock_virtual[
        (stock_virtual["Referencia"] == referencia)
        & (stock_virtual["Stock"] > 0)
    ].sort_values("Caducidad")

    if candidatos.empty:
        return pd.NaT, 0, "Rotura!"

    disponible = candidatos["Stock"].sum()

    if disponible < cantidad:
        return candidatos.iloc[0]["Caducidad"], disponible, "Rotura!"

    fecha_propuesta = candidatos.iloc[0]["Caducidad"]

    pendiente = cantidad

    for idx in candidatos.index:
        stock_linea = stock_virtual.loc[idx, "Stock"]
        consumo = min(stock_linea, pendiente)

        stock_virtual.loc[idx, "Stock"] -= consumo
        pendiente -= consumo

        if pendiente <= 0:
            break

    return fecha_propuesta, disponible, "OK"


def normalizar_id(serie):
    """
    Convierte IDs numéricos tipo 2607.0 a string '2607',
    manteniendo nulos como <NA>.
    """
    return pd.to_numeric(serie, errors="coerce").astype("Int64").astype("string")


def normalizar_referencia(serie):
    """
    Convierte referencias a texto limpio.
    Ejemplo:
        5439.0 -> 5439
        ' 5439 ' -> 5439
    """
    return (
        serie
        .fillna("")
        .astype(str)
        .str.strip()
        .str.replace(r"\.0$", "", regex=True)
    )


def consumir_stock_mayor_igual(stock_virtual, referencia, fecha_minima, cantidad):
    """
    Consume stock de una referencia usando caducidades >= fecha_minima.
    Consume FIFO por caducidad.
    Si no hay fecha mínima y hay cantidad, se considera Rotura.
    Si no hay stock suficiente para servir íntegramente, NO descuenta stock.
    """

    if cantidad <= 0:
        return pd.NaT, 0, ""

    if cantidad <= 0:
        return pd.NaT, 0, ""

    if pd.isna(fecha_minima):
        return pd.NaT, 0, "Rotura!"

    candidatos = stock_virtual[
        (stock_virtual["Referencia"] == referencia)
        & (stock_virtual["Caducidad"] >= fecha_minima)
        & (stock_virtual["Stock"] > 0)
    ].sort_values("Caducidad")

    if candidatos.empty:
        return pd.NaT, 0, "Rotura!"

    disponible = candidatos["Stock"].sum()

    if disponible < cantidad:
        return candidatos.iloc[0]["Caducidad"], disponible, "Rotura!"

    fecha_propuesta = candidatos.iloc[0]["Caducidad"]

    pendiente = cantidad

    for idx in candidatos.index:
        stock_linea = stock_virtual.loc[idx, "Stock"]
        consumo = min(stock_linea, pendiente)

        stock_virtual.loc[idx, "Stock"] -= consumo
        pendiente -= consumo

        if pendiente <= 0:
            break

    return fecha_propuesta, disponible, "OK"


def consumir_stock_exacto(stock_virtual, referencia, fecha_exacta, cantidad):
    """
    Primero intenta servir íntegramente con la fecha exacta.
    Si no puede, propone la siguiente fecha superior y consume desde ahí en adelante.
    Si no hay fecha exacta y hay cantidad, se considera Rotura.
    Si no hay stock suficiente para servir íntegramente, NO descuenta stock.
    """

    if cantidad <= 0:
        return pd.NaT, 0, ""

    if pd.isna(fecha_exacta):
        return pd.NaT, 0, "Rotura!"

    exacta = stock_virtual[
        (stock_virtual["Referencia"] == referencia)
        & (stock_virtual["Caducidad"] == fecha_exacta)
        & (stock_virtual["Stock"] > 0)
    ].sort_values("Caducidad")

    stock_exacto = exacta["Stock"].sum()

    if stock_exacto >= cantidad:
        pendiente = cantidad

        for idx in exacta.index:
            stock_linea = stock_virtual.loc[idx, "Stock"]
            consumo = min(stock_linea, pendiente)

            stock_virtual.loc[idx, "Stock"] -= consumo
            pendiente -= consumo

            if pendiente <= 0:
                break

        return fecha_exacta, stock_exacto, "OK"

    posteriores = stock_virtual[
        (stock_virtual["Referencia"] == referencia)
        & (stock_virtual["Caducidad"] > fecha_exacta)
        & (stock_virtual["Stock"] > 0)
    ].sort_values("Caducidad")

    if posteriores.empty:
        return pd.NaT, stock_exacto, "Rotura!"

    disponible_posterior = posteriores["Stock"].sum()

    if disponible_posterior < cantidad:
        return posteriores.iloc[0]["Caducidad"], disponible_posterior, "Rotura!"

    fecha_propuesta = posteriores.iloc[0]["Caducidad"]

    pendiente = cantidad

    for idx in posteriores.index:
        stock_linea = stock_virtual.loc[idx, "Stock"]
        consumo = min(stock_linea, pendiente)

        stock_virtual.loc[idx, "Stock"] -= consumo
        pendiente -= consumo

        if pendiente <= 0:
            break

    return fecha_propuesta, disponible_posterior, "OK"


def cruce_archivos(archivo_pedidos, archivo_fcp, archivo_stock, almacen):

    date = time.strftime("%Y%m%d%H%M%S")

    engine = create_engine("mssql+pyodbc://@XGA_PROD")
    engine_sqlite = create_engine(f"sqlite:///{DB_FILE}")

    # =========================
    # 1) Lectura de archivos
    # =========================

    df_pedidos = pd.read_csv(
        archivo_pedidos,
        sep=";",
        encoding="utf-8-sig",
        dtype=str
    )

    df_fcp = pd.read_excel(
        archivo_fcp,
        engine="openpyxl",
        sheet_name="Datos",
        dtype=str
    )

    df_stock = pd.read_excel(
        archivo_stock,
        engine="openpyxl",
        sheet_name="Sheet1",
        dtype=str
    )

    df_pedidos.columns = df_pedidos.columns.str.strip()
    df_fcp.columns = df_fcp.columns.str.strip()
    df_stock.columns = df_stock.columns.str.strip()

    # =========================
    # 2) Cruce pedidos vs FCP
    # =========================

    df_pedidos["Albarán"] = df_pedidos["Albarán"].fillna("").astype(str).str.strip()
    df_pedidos["Referencia"] = normalizar_referencia(df_pedidos["Referencia"])

    df_fcp["Pedido"] = df_fcp["Pedido"].fillna("").astype(str).str.strip()
    df_fcp["Referencia"] = normalizar_referencia(df_fcp["Referencia"])

    columnas_fcp = [
        "Pedido",
        "Referencia",
        "FCP Mayor o igual",
        "FCP Exactamente igual",
        "FCP según % vida útil"
    ]

    # Nos quedamos solo con las columnas necesarias
    df_fcp_cruce = df_fcp[columnas_fcp].copy()

    # Limpiar vacíos
    for col in [
        "FCP Mayor o igual",
        "FCP Exactamente igual",
        "FCP según % vida útil"
    ]:
        df_fcp_cruce[col] = (
            df_fcp_cruce[col]
            .replace("", pd.NA)
            .replace("nan", pd.NA)
            .replace("None", pd.NA)
        )

    # Agrupar para que haya UNA sola línea por Pedido + Referencia
    # y conservar el primer valor informado de cada FCP
    df_fcp_cruce = (
        df_fcp_cruce
        .groupby(["Pedido", "Referencia"], as_index=False)
        .agg({
            "FCP Mayor o igual": "first",
            "FCP Exactamente igual": "first",
            "FCP según % vida útil": "first"
        })
    )

    # Control: ahora este merge debe ser muchos-a-uno
    df_cruce = df_pedidos.merge(
        df_fcp_cruce,
        left_on=["Albarán", "Referencia"],
        right_on=["Pedido", "Referencia"],
        how="left",
        validate="m:1"
    )

    df_cruce = df_cruce.drop(columns=["Pedido"], errors="ignore")
    
    # =========================
    # 3) Obtener stock SQL Server para maestro de fechas
    # =========================

    query_stock_prod = text("""
        SELECT
            RTRIM(CodigoProdClte) AS Referencia,
            NombreProdClte,
            FechaProduccionPalet,
            SUM(CantidadActualPalet) AS Stock 
        FROM
            vPalets
        WHERE
            ID_Cliente = 944
            AND ID_Almacen = :almacen
            AND CantidadActualPalet > 0
            AND ID_EstadoProd = 1
        GROUP BY
            RTRIM(CodigoProdClte),
            NombreProdClte,
            FechaProduccionPalet
    """)

    with engine.connect() as conn:
        df1 = pd.read_sql(query_stock_prod, conn, params={"almacen": almacen})

    # =========================
    # 4) Obtener maestro SQLite
    # =========================

    query_maestro = text("""
        SELECT
            ID_ProdClte,
            RTRIM(CodigoProdClte) AS Referencia,
            CodigoUnidad,
            DiasCaducidadProdClte,
            ID_ProdClteSustitutivo 
        FROM
            maestro_msm
    """)

    with engine_sqlite.connect() as conn:
        df_maestro = pd.read_sql(query_maestro, conn)

    engine.dispose()
    engine_sqlite.dispose()

    df1.columns = df1.columns.str.strip()
    df_maestro.columns = df_maestro.columns.str.strip()

    df1["Referencia"] = normalizar_referencia(df1["Referencia"])
    df_maestro["Referencia"] = normalizar_referencia(df_maestro["Referencia"])

    df_maestro["ID_ProdClte"] = normalizar_id(df_maestro["ID_ProdClte"])
    df_maestro["ID_ProdClteSustitutivo"] = normalizar_id(df_maestro["ID_ProdClteSustitutivo"])

    # =========================
    # 5) Cruzar stock SQL con maestro
    # =========================

    df_1maestro = df1.merge(
        df_maestro,
        on="Referencia",
        how="left"
    )

    # =========================
    # 6) Obtener referencia sustitutiva
    # =========================

    df_sustitutivos = (
        df_maestro[["ID_ProdClte", "Referencia"]]
        .dropna(subset=["ID_ProdClte"])
        .drop_duplicates(subset=["ID_ProdClte"])
        .rename(columns={
            "ID_ProdClte": "ID_ProdClteSustitutivo",
            "Referencia": "ReferenciaSustitutiva"
        })
    )

    # =========================
    # Sustitutivo inverso
    # Si una referencia actual es la referencia sustitutiva de otra,
    # buscamos la referencia "hija"
    # =========================

    df_sustitutivos_inverso = (
        df_maestro[[
            "ID_ProdClte",
            "Referencia",
            "ID_ProdClteSustitutivo"
        ]]
        .dropna(subset=["ID_ProdClteSustitutivo"])
        .copy()
    )

    # Tabla auxiliar ID_ProdClte -> Referencia padre
    df_id_ref = (
        df_maestro[["ID_ProdClte", "Referencia"]]
        .dropna(subset=["ID_ProdClte"])
        .drop_duplicates(subset=["ID_ProdClte"])
        .rename(columns={
            "ID_ProdClte": "ID_ProdClteSustitutivo",
            "Referencia": "ReferenciaPadre"
        })
    )

    df_sustitutivos_inverso = df_sustitutivos_inverso.merge(
        df_id_ref,
        on="ID_ProdClteSustitutivo",
        how="left"
    )

    df_sustitutivos_inverso = (
        df_sustitutivos_inverso[[
            "ReferenciaPadre",
            "Referencia"
        ]]
        .dropna(subset=["ReferenciaPadre"])
        .drop_duplicates(subset=["ReferenciaPadre"])
        .rename(columns={
            "ReferenciaPadre": "Referencia",
            "Referencia": "ReferenciaSustitutivaInversa"
        })
    )

    df_1maestro = df_1maestro.merge(
        df_sustitutivos,
        on="ID_ProdClteSustitutivo",
        how="left"
    )

    df_1maestro["ReferenciaSustitutiva"] = df_1maestro["ReferenciaSustitutiva"].fillna("")

    # =========================
    # 7) Calcular FechaCaducidadCalculada
    # =========================

    df_1maestro["FechaProduccionPalet"] = pd.to_datetime(
        df_1maestro["FechaProduccionPalet"],
        errors="coerce"
    )

    df_1maestro["DiasCaducidadProdClte"] = pd.to_numeric(
        df_1maestro["DiasCaducidadProdClte"],
        errors="coerce"
    )

    df_1maestro["FechaCaducidadCalculada"] = (
        df_1maestro["FechaProduccionPalet"]
        + pd.to_timedelta(df_1maestro["DiasCaducidadProdClte"], unit="D")
    )

    # =========================
    # 8) Quedarse con producción más antigua por Referencia
    # =========================

    df_1maestro["Referencia"] = normalizar_referencia(df_1maestro["Referencia"])
    df_cruce["Referencia"] = normalizar_referencia(df_cruce["Referencia"])

    df_maestro_antiguo = (
        df_1maestro
        .sort_values(["Referencia", "FechaProduccionPalet"])
        .drop_duplicates(subset=["Referencia"], keep="first")
        [[
            "Referencia",
            "CodigoUnidad",
            "FechaProduccionPalet",
            "FechaCaducidadCalculada",
            "DiasCaducidadProdClte",
            "ID_ProdClteSustitutivo",
            "ReferenciaSustitutiva"
        ]]
        .copy()
    )

    # =========================
    # 9) Cruzar df_cruce con maestro antiguo
    # =========================

    df_cruce = df_cruce.merge(
        df_maestro_antiguo,
        on="Referencia",
        how="left"
    )

    df_cruce = df_cruce.merge(
    df_sustitutivos_inverso,
    on="Referencia",
    how="left"
    )

    df_cruce["ReferenciaSustitutivaInversa"] = (
        df_cruce["ReferenciaSustitutivaInversa"]
        .fillna("")
        .astype(str)
        .str.strip()
    )

    df_cruce["ReferenciaSustitutiva"] = df_cruce["ReferenciaSustitutiva"].fillna("")

    # =========================
    # 10) Calcular FechaCaducidadSegunPorcentaje
    # =========================

    porcentaje = (
        df_cruce["FCP según % vida útil"]
        .astype(str)
        .str.replace("%", "", regex=False)
        .str.replace(",", ".", regex=False)
        .str.strip()
    )

    porcentaje = pd.to_numeric(porcentaje, errors="coerce")
    porcentaje = porcentaje.where(porcentaje <= 1, porcentaje / 100)

    df_cruce["FechaCaducidadSegunPorcentaje"] = pd.NaT

    mask_porcentaje = porcentaje.notna()

    df_cruce.loc[mask_porcentaje, "FechaCaducidadSegunPorcentaje"] = (
        df_cruce.loc[mask_porcentaje, "FechaProduccionPalet"]
        + pd.to_timedelta(
            (
                df_cruce.loc[mask_porcentaje, "DiasCaducidadProdClte"]
                * porcentaje.loc[mask_porcentaje]
            ).round(),
            unit="D"
        )
    )

    # Limpiar columna técnica si no la quieres ver
    df_cruce = df_cruce.drop(
        columns=["ID_ProdClteSustitutivo"],
        errors="ignore"
    )

    # =========================
    # 11) Preparar datos para simulación de stock
    # =========================

    df_cruce["Palets"] = pd.to_numeric(
        df_cruce["Palets"],
        errors="coerce"
    ).fillna(0)

    df_cruce["Referencia"] = normalizar_referencia(df_cruce["Referencia"])

    df_stock["Referencia"] = normalizar_referencia(df_stock["Referencia"])

    df_stock["Caducidad"] = pd.to_datetime(
        df_stock["Caducidad"],
        errors="coerce"
    )

    df_stock["Stock"] = pd.to_numeric(
        df_stock["Stock"],
        errors="coerce"
    ).fillna(0)

    # Normalizar fechas de condiciones
    for col in [
        "FCP Mayor o igual",
        "FCP Exactamente igual",
        "FechaCaducidadSegunPorcentaje"
    ]:
        if col in df_cruce.columns:
            df_cruce[col] = pd.to_datetime(
                df_cruce[col],
                dayfirst=True,
                errors="coerce"
            )

    # =========================
    # 12) ÚNICO stock virtual compartido
    # =========================

    stock_virtual = df_stock.copy()

   # =========================
    # 13) Crear columnas resultado
    # =========================

    df_cruce["FechaPropuesta_MayorIgual"] = pd.NaT
    df_cruce["StockDisponible_MayorIgual"] = 0
    df_cruce["Resultado_MayorIgual"] = ""

    df_cruce["FechaPropuesta_Exacta"] = pd.NaT
    df_cruce["StockDisponible_Exacta"] = 0
    df_cruce["Resultado_Exacta"] = ""

    df_cruce["FechaPropuesta_Porcentaje"] = pd.NaT
    df_cruce["StockDisponible_Porcentaje"] = 0
    df_cruce["Resultado_Porcentaje"] = ""

    df_cruce["FechaPropuesta_SinFCP"] = pd.NaT
    df_cruce["StockDisponible_SinFCP"] = 0
    df_cruce["Resultado_SinFCP"] = ""

    df_cruce["CriterioAplicado"] = ""
    df_cruce["FechaPropuesta_Final"] = pd.NaT
    df_cruce["StockDisponible_Final"] = 0
    df_cruce["Resultado_Final"] = ""


    # =========================
    # 14) Procesar pedidos una sola vez
    # =========================

    for idx, fila in df_cruce.iterrows():

        referencia = str(fila["Referencia"]).strip()
        cantidad = fila["Palets"]

        fcp_mayor = fila["FCP Mayor o igual"]
        fcp_exacta = fila["FCP Exactamente igual"]
        fcp_porcentaje = fila["FechaCaducidadSegunPorcentaje"]

        # =========================
        # Prioridad 1: FCP Exactamente igual
        # =========================
        if pd.notna(fcp_exacta):

            fecha, stock, estado = consumir_stock_exacto(
                stock_virtual,
                referencia,
                fcp_exacta,
                cantidad
            )

            df_cruce.loc[idx, "FechaPropuesta_Exacta"] = fecha
            df_cruce.loc[idx, "StockDisponible_Exacta"] = stock
            df_cruce.loc[idx, "Resultado_Exacta"] = estado

            df_cruce.loc[idx, "CriterioAplicado"] = "FCP Exactamente igual"
            df_cruce.loc[idx, "FechaPropuesta_Final"] = fecha
            df_cruce.loc[idx, "StockDisponible_Final"] = stock
            df_cruce.loc[idx, "Resultado_Final"] = estado

        # =========================
        # Prioridad 2: FCP Mayor o igual
        # =========================
        elif pd.notna(fcp_mayor):

            fecha, stock, estado = consumir_stock_mayor_igual(
                stock_virtual,
                referencia,
                fcp_mayor,
                cantidad
            )

            df_cruce.loc[idx, "FechaPropuesta_MayorIgual"] = fecha
            df_cruce.loc[idx, "StockDisponible_MayorIgual"] = stock
            df_cruce.loc[idx, "Resultado_MayorIgual"] = estado

            df_cruce.loc[idx, "CriterioAplicado"] = "FCP Mayor o igual"
            df_cruce.loc[idx, "FechaPropuesta_Final"] = fecha
            df_cruce.loc[idx, "StockDisponible_Final"] = stock
            df_cruce.loc[idx, "Resultado_Final"] = estado

        # =========================
        # Prioridad 3: FCP según % vida útil
        # =========================
        elif pd.notna(fcp_porcentaje):

            fecha, stock, estado = consumir_stock_mayor_igual(
                stock_virtual,
                referencia,
                fcp_porcentaje,
                cantidad
            )

            df_cruce.loc[idx, "FechaPropuesta_Porcentaje"] = fecha
            df_cruce.loc[idx, "StockDisponible_Porcentaje"] = stock
            df_cruce.loc[idx, "Resultado_Porcentaje"] = estado

            df_cruce.loc[idx, "CriterioAplicado"] = "FCP según % vida útil"
            df_cruce.loc[idx, "FechaPropuesta_Final"] = fecha
            df_cruce.loc[idx, "StockDisponible_Final"] = stock
            df_cruce.loc[idx, "Resultado_Final"] = estado

        # =========================
        # Prioridad 4: Sin FCP
        # Consumir desde la fecha más antigua
        # =========================
        else:

            fecha, stock, estado = consumir_stock_sin_restriccion(
                stock_virtual,
                referencia,
                cantidad
            )

            df_cruce.loc[idx, "FechaPropuesta_SinFCP"] = fecha
            df_cruce.loc[idx, "StockDisponible_SinFCP"] = stock
            df_cruce.loc[idx, "Resultado_SinFCP"] = estado

            df_cruce.loc[idx, "CriterioAplicado"] = "Sin FCP - fecha más antigua"
            df_cruce.loc[idx, "FechaPropuesta_Final"] = fecha
            df_cruce.loc[idx, "StockDisponible_Final"] = stock
            df_cruce.loc[idx, "Resultado_Final"] = estado

    # =========================
    # 16.5) Comprobar motivos rotura
    # =========================
    df_cruce["MotivoRotura"] = ""

    df_cruce.loc[
        df_cruce["Resultado_Final"] == "Rotura!",
        "MotivoRotura"
    ] = "Stock insuficiente"


    # =========================
    # 17) Formatear fechas para exportar
    # =========================

    columnas_fecha_export = [
        "FCP_SustitutivaInversa",
        "FCP Mayor o igual",
        "FCP Exactamente igual",
        "FechaProduccionPalet",
        "FechaCaducidadCalculada",
        "FechaCaducidadSegunPorcentaje",
        "FechaPropuesta_MayorIgual",
        "FechaPropuesta_Exacta",
        "FechaPropuesta_Porcentaje",
        "FechaPropuesta_SinFCP",
        "FechaPropuesta_Final",        
        "FCP_SustitutivaDisponible"


    ]

    # =========================
    # 18) Buscar stock de referencia sustitutiva inversa
    # =========================

    # =========================
    # Buscar stock de referencias sustitutivas
    # Directa e inversa
    # =========================

    df_cruce["ReferenciaSustitutivaUsada"] = ""
    df_cruce["TipoReferenciaSustitutiva"] = ""
    df_cruce["FCP_SustitutivaDisponible"] = pd.NaT
    df_cruce["Stock_SustitutivaDisponible"] = 0

    # Normalizar por seguridad
    for col in ["ReferenciaSustitutiva", "ReferenciaSustitutivaInversa"]:
        if col in df_cruce.columns:
            df_cruce[col] = (
                df_cruce[col]
                .fillna("")
                .astype(str)
                .str.strip()
                .str.replace(r"\.0$", "", regex=True)
            )

    for idx, fila in df_cruce.iterrows():

        # Fecha requerida para comparar la alternativa
        # Prioridad:
        # 1. FCP Exactamente igual
        # 2. FCP Mayor o igual
        # 3. Fecha calculada por porcentaje
        # 4. FechaCaducidadCalculada
        # 5. Sin fecha, buscar más antigua
        if pd.notna(fila.get("FCP Exactamente igual")):
            fecha_requerida = fila.get("FCP Exactamente igual")

        elif pd.notna(fila.get("FCP Mayor o igual")):
            fecha_requerida = fila.get("FCP Mayor o igual")

        elif pd.notna(fila.get("FechaCaducidadSegunPorcentaje")):
            fecha_requerida = fila.get("FechaCaducidadSegunPorcentaje")

        elif pd.notna(fila.get("FechaCaducidadCalculada")):
            fecha_requerida = fila.get("FechaCaducidadCalculada")

        else:
            fecha_requerida = pd.NaT

        referencias_a_probar = []

        ref_sustitutiva = str(fila.get("ReferenciaSustitutiva", "")).strip()
        ref_sustitutiva_inversa = str(fila.get("ReferenciaSustitutivaInversa", "")).strip()

        if ref_sustitutiva != "":
            referencias_a_probar.append(("Directa", ref_sustitutiva))

        if ref_sustitutiva_inversa != "":
            referencias_a_probar.append(("Inversa", ref_sustitutiva_inversa))

        for tipo_ref, referencia_alt in referencias_a_probar:

            fecha_alt, stock_alt = buscar_stock_referencia_alternativa(
                stock_virtual,
                referencia_alt,
                fecha_requerida
            )

            if pd.notna(fecha_alt) and stock_alt > 0:

                df_cruce.loc[idx, "ReferenciaSustitutivaUsada"] = referencia_alt
                df_cruce.loc[idx, "TipoReferenciaSustitutiva"] = tipo_ref
                df_cruce.loc[idx, "FCP_SustitutivaDisponible"] = fecha_alt
                df_cruce.loc[idx, "Stock_SustitutivaDisponible"] = stock_alt

                break

    for idx, fila in df_cruce.iterrows():

        referencia_inversa = str(
            fila.get("ReferenciaSustitutivaInversa", "")
        ).strip()

        if referencia_inversa == "":
            continue

        # Fecha requerida según el criterio aplicado
        criterio = str(fila.get("CriterioAplicado", "")).strip()

        if criterio == "FCP Exactamente igual":
            fecha_requerida = fila.get("FCP Exactamente igual")

        elif criterio == "FCP Mayor o igual":
            fecha_requerida = fila.get("FCP Mayor o igual")

        elif criterio == "FCP según % vida útil":
            fecha_requerida = fila.get("FechaCaducidadSegunPorcentaje")

        else:
            # Si no tiene FCP, buscamos desde la fecha más antigua
            fecha_requerida = pd.NaT

        fecha_inv, stock_inv = buscar_stock_referencia_inversa(
            stock_virtual,
            referencia_inversa,
            fecha_requerida
        )

        df_cruce.loc[idx, "FCP_SustitutivaInversa"] = fecha_inv
        df_cruce.loc[idx, "Stock_SustitutivaInversa"] = stock_inv

    df_export = df_cruce.copy()

    
    # =========================
    # Ordenar por Fecha de Carga
    # Primero vacíos, luego de anterior a posterior
    # =========================

    if "Fecha de Carga" in df_export.columns:

        fecha_carga_dt = pd.to_datetime(
            df_export["Fecha de Carga"],
            errors="coerce",
            dayfirst=True
        )

        df_export["_FechaCargaVacia"] = fecha_carga_dt.isna()
        df_export["_FechaCargaOrden"] = fecha_carga_dt

        df_export = (
            df_export
            .sort_values(
                by=["_FechaCargaVacia", "_FechaCargaOrden"],
                ascending=[False, True],
                kind="mergesort"
            )
            .drop(columns=["_FechaCargaVacia", "_FechaCargaOrden"])
            .reset_index(drop=True)
        )


    # =========================
    # Formatear fechas para exportar
    # =========================



    for col in columnas_fecha_export:
        if col in df_export.columns:
            df_export[col] = pd.to_datetime(
                df_export[col],
                errors="coerce"
            ).dt.strftime("%d/%m/%Y")

    df_export = df_export.fillna("")

    # =========================
    # 18) Exportar Excel con formato
    # =========================

    if almacen == 129:
        path_file = f"C:\\Users\\{USER}\\GXO\\SPALOVERA4 - OPERACIONES\\Control Stock\\FALTAS\\Archivos Raw\\Interim"
    if almacen == 221:
        path_file = f"C:\\Users\\{USER}\\GXO\\SPALOVERA4 - OPERACIONES\\Control Stock\\FALTAS\\Archivos Raw\\Steel"
    output_file = f"cruce_pedidos_{date}.xlsx"
    output_file = os.path.join(path_file, output_file)

    with pd.ExcelWriter(output_file, engine="xlsxwriter") as writer:

        df_export.to_excel(writer, index=False, sheet_name="Datos")

        workbook = writer.book
        worksheet = writer.sheets["Datos"]

        formato_rotura = workbook.add_format({
            "bg_color": "#FF9999"
        })

        formato_fecha_borde = workbook.add_format({            
            "top": 2,
            "bottom": 2,
            "left": 2,
            "right": 2,
            "top_color": "red",
            "bottom_color": "red",
            "left_color": "red",
            "right_color": "red"
            })


        columnas = {
            col: idx
            for idx, col in enumerate(df_export.columns)
        }

        ultima_fila = len(df_export)
        ultima_columna = len(df_export.columns) - 1

        # ==========================
        # Fila completa roja si hay Rotura!
        # ==========================

        for col_resultado in [
        "Resultado_Final"
        ]:
            if col_resultado in columnas:

                col_idx = columnas[col_resultado]
                col_excel = xl_col_to_name(col_idx)

                worksheet.conditional_format(
                    1,
                    0,
                    ultima_fila,
                    ultima_columna,
                    {
                        "type": "formula",
                        "criteria": f'=${col_excel}2="Rotura!"',
                        "format": formato_rotura
                    }
                )

        # ==========================
        # Bordes rojos en línea completa SOLO si:
        # - El cliente ha informado FCP
        # - Y la fecha propuesta es distinta
        # ==========================

        def valor_valido_excel(valor):
            valor = str(valor).strip()
            return valor not in ["", "nan", "NaT", "None"]


        for idx, fila in df_export.iterrows():

            fila_excel = idx + 1  # type: ignore fila 0 son cabeceras
            marcar_borde = False

            criterio = str(fila.get("CriterioAplicado", "")).strip()

            # ==========================
            # FCP Mayor o igual
            # ==========================
            if criterio == "FCP Mayor o igual":

                fcp_cliente = fila.get("FCP Mayor o igual", "")
                fecha_propuesta = fila.get("FechaPropuesta_MayorIgual", "")

                if (
                    valor_valido_excel(fcp_cliente)
                    and valor_valido_excel(fecha_propuesta)
                    and str(fcp_cliente).strip() != str(fecha_propuesta).strip()
                ):
                    marcar_borde = True

            # ==========================
            # FCP Exactamente igual
            # ==========================
            elif criterio == "FCP Exactamente igual":

                fcp_cliente = fila.get("FCP Exactamente igual", "")
                fecha_propuesta = fila.get("FechaPropuesta_Exacta", "")

                if (
                    valor_valido_excel(fcp_cliente)
                    and valor_valido_excel(fecha_propuesta)
                    and str(fcp_cliente).strip() != str(fecha_propuesta).strip()
                ):
                    marcar_borde = True

            # ==========================
            # FCP según % vida útil
            # ==========================
            elif criterio == "FCP según % vida útil":

                fcp_calculada = fila.get("FechaCaducidadSegunPorcentaje", "")
                fecha_propuesta = fila.get("FechaPropuesta_Porcentaje", "")

                if (
                    valor_valido_excel(fcp_calculada)
                    and valor_valido_excel(fecha_propuesta)
                    and str(fcp_calculada).strip() != str(fecha_propuesta).strip()
                ):
                    marcar_borde = True

            # ==========================
            # Si es Sin FCP, NO marcamos borde
            # ==========================
            # criterio == "Sin FCP - fecha más antigua" -> sin borde

            if marcar_borde:
                marcar_fila_borde_rojo(
                    worksheet,
                    fila_excel,
                    ultima_columna,
                    formato_fecha_borde
                )

        # ==========================
        # Autoajustar columnas
        # ==========================

        for i, col in enumerate(df_export.columns):

            try:
                ancho_datos = (
                    df_export[col]
                    .fillna("")
                    .astype(str)
                    .str.len()
                    .max()
                )

                ancho = max(len(str(col)), ancho_datos) + 2

            except Exception:
                ancho = len(str(col)) + 2

            worksheet.set_column(i, i, min(ancho, 50))

    print("OK ->", output_file)

    return df_cruce


if __name__ == "__main__":

    df_resultado = cruce_archivos(
        archivo_pedidos=r"C:\Users\jgmeras\OneDrive - GXO\Documents\Python Scripts\01. MAHOU\Stock\pedidos_20260707150357.csv",
        archivo_fcp=r"C:\Users\jgmeras\OneDrive - GXO\Documents\Python Scripts\01. MAHOU\Stock\parsed_edis_20260707150413.xlsx",
        archivo_stock=r"C:\Users\jgmeras\OneDrive - GXO\Documents\Python Scripts\01. MAHOU\Stock\vUbicacionesProducto_20260707150414.xlsx",
        almacen=almacen
    )