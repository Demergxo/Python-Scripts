import os
import pandas as pd
from sqlalchemy import create_engine, text
import time

path = os.getcwd()
DB_FILE = os.path.join(path, "apoyo.db")

almacen = 221


def normalizar_id(serie):
    """
    Convierte IDs numéricos tipo 2607.0 a string '2607',
    manteniendo nulos como <NA>.
    """
    return pd.to_numeric(serie, errors="coerce").astype("Int64").astype("string")

def buscar_fcp_mayor_igual(df_stock_ref, fecha_minima, cantidad):

    if pd.isna(fecha_minima):
        return "", 0, ""

    candidatos = (
        df_stock_ref[
            df_stock_ref["Caducidad"] >= fecha_minima
        ]
        .sort_values("Caducidad")
    )

    if candidatos.empty:
        return "", 0, "Rotura!"

    stock_total = candidatos["Stock"].sum()

    fecha_propuesta = candidatos.iloc[0]["Caducidad"]

    if stock_total >= cantidad:
        return fecha_propuesta, stock_total, "OK"

    return fecha_propuesta, stock_total, "Rotura!"

def buscar_fcp_exacta(df_stock_ref, fecha_objetivo, cantidad):

    if pd.isna(fecha_objetivo):
        return "", 0, ""

    exacta = df_stock_ref[
        df_stock_ref["Caducidad"] == fecha_objetivo
    ]

    stock_exacto = exacta["Stock"].sum()

    if stock_exacto >= cantidad:
        return fecha_objetivo, stock_exacto, "OK"

    posteriores = (
        df_stock_ref[
            df_stock_ref["Caducidad"] > fecha_objetivo
        ]
        .sort_values("Caducidad")
    )

    stock_total = stock_exacto + posteriores["Stock"].sum()

    if stock_total >= cantidad and not posteriores.empty:

        return (
            posteriores.iloc[0]["Caducidad"],
            stock_total,
            "OK"
        )

    return "", stock_total, "Rotura!"

def consumir_stock(stock_virtual, referencia, fecha_minima, cantidad):
    
    if pd.isna(fecha_minima):
        return "", 0, ""

    candidatos = stock_virtual[
        (stock_virtual["Referencia"] == referencia)
        & (stock_virtual["Caducidad"] >= fecha_minima)
        & (stock_virtual["Stock"] > 0)
    ].sort_values("Caducidad")

    if candidatos.empty:
        return "", 0, "Rotura!"

    disponible = candidatos["Stock"].sum()

    fecha_propuesta = candidatos.iloc[0]["Caducidad"]

    pendiente = cantidad

    for idx in candidatos.index:

        stock_linea = stock_virtual.loc[idx, "Stock"]

        consumo = min(stock_linea, pendiente)

        stock_virtual.loc[idx, "Stock"] -= consumo

        pendiente -= consumo

        if pendiente <= 0:
            break

    if pendiente > 0:
        return fecha_propuesta, disponible, "Rotura!"

    return fecha_propuesta, disponible, "OK"

def consumir_stock_exacto(stock_virtual, referencia, fecha_exacta, cantidad):

    if pd.isna(fecha_exacta):
        return "", 0, ""

    candidatos = stock_virtual[
        (stock_virtual["Referencia"] == referencia)
        & (stock_virtual["Caducidad"] >= fecha_exacta)
        & (stock_virtual["Stock"] > 0)
    ].sort_values("Caducidad")

    if candidatos.empty:
        return "", 0, "Rotura!"

    disponible = candidatos["Stock"].sum()

    fecha_propuesta = candidatos.iloc[0]["Caducidad"]

    pendiente = cantidad

    for idx in candidatos.index:

        stock_linea = stock_virtual.loc[idx, "Stock"]

        consumo = min(stock_linea, pendiente)

        stock_virtual.loc[idx, "Stock"] -= consumo

        pendiente -= consumo

        if pendiente <= 0:
            break

    if pendiente > 0:
        return fecha_propuesta, disponible, "Rotura!"

    return fecha_propuesta, disponible, "OK"




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

    # Limpiar nombres de columnas
    df_pedidos.columns = df_pedidos.columns.str.strip()
    df_fcp.columns = df_fcp.columns.str.strip()
    df_stock.columns = df_stock.columns.str.strip()

    # =========================
    # 2) Cruce pedidos vs FCP
    # =========================

    df_pedidos["Albarán"] = df_pedidos["Albarán"].fillna("").astype(str).str.strip()
    df_pedidos["Referencia"] = df_pedidos["Referencia"].fillna("").astype(str).str.strip()

    df_fcp["Pedido"] = df_fcp["Pedido"].fillna("").astype(str).str.strip()
    df_fcp["Referencia"] = df_fcp["Referencia"].fillna("").astype(str).str.strip()

    columnas_fcp = [
        "Pedido",
        "Referencia",
        "FCP Mayor o igual",
        "FCP Exactamente igual",
        "FCP según % vida útil"
    ]

    df_cruce = df_pedidos.merge(
        df_fcp[columnas_fcp],
        left_on=["Albarán", "Referencia"],
        right_on=["Pedido", "Referencia"],
        how="left"
    )

    df_cruce = df_cruce.drop(columns=["Pedido"], errors="ignore")

    # =========================
    # 3) Obtener stock SQL Server
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

    # Limpiar columnas
    df1.columns = df1.columns.str.strip()
    df_maestro.columns = df_maestro.columns.str.strip()

    df1["Referencia"] = df1["Referencia"].fillna("").astype(str).str.strip()
    df_maestro["Referencia"] = df_maestro["Referencia"].fillna("").astype(str).str.strip()

    # Normalizar IDs
    df_maestro["ID_ProdClte"] = normalizar_id(df_maestro["ID_ProdClte"])
    df_maestro["ID_ProdClteSustitutivo"] = normalizar_id(df_maestro["ID_ProdClteSustitutivo"])

    # =========================
    # 5) Cruzar stock con maestro
    # =========================

    df_1maestro = df1.merge(
        df_maestro,
        on="Referencia",
        how="left"
    )

    # =========================
    # 6) Obtener referencia sustitutiva
    # =========================
    # ID_ProdClteSustitutivo -> ID_ProdClte del maestro -> Referencia real

    df_sustitutivos = (
        df_maestro[["ID_ProdClte", "Referencia"]]
        .dropna(subset=["ID_ProdClte"])
        .drop_duplicates(subset=["ID_ProdClte"])
        .rename(columns={
            "ID_ProdClte": "ID_ProdClteSustitutivo",
            "Referencia": "ReferenciaSustitutiva"
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
        df_1maestro["FechaProduccionPalet"] +
        pd.to_timedelta(df_1maestro["DiasCaducidadProdClte"], unit="D")
    )

    # =========================
    # 8) Quedarse con producción más antigua por Referencia
    # =========================

    df_1maestro["Referencia"] = df_1maestro["Referencia"].fillna("").astype(str).str.strip()
    df_cruce["Referencia"] = df_cruce["Referencia"].fillna("").astype(str).str.strip()

    df_maestro_antiguo = (
        df_1maestro
        .sort_values(["Referencia", "FechaProduccionPalet"])
        .drop_duplicates(subset=["Referencia"], keep="first")
        [[
            "Referencia",
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

    # Si viene 67, lo convierte a 0.67.
    # Si viene 0.67, lo deja como 0.67.
    porcentaje = porcentaje.where(porcentaje <= 1, porcentaje / 100)

    df_cruce["FechaCaducidadSegunPorcentaje"] = pd.NaT

    mask_porcentaje = porcentaje.notna()

    df_cruce.loc[mask_porcentaje, "FechaCaducidadSegunPorcentaje"] = (
        df_cruce.loc[mask_porcentaje, "FechaProduccionPalet"] +
        pd.to_timedelta(
            (
                df_cruce.loc[mask_porcentaje, "DiasCaducidadProdClte"] *
                porcentaje.loc[mask_porcentaje]
            ).round(),
            unit="D"
        )
    )

    # =========================
    # 11) Limpieza final opcional
    # =========================

    # Si quieres que los IDs vacíos no salgan como <NA>
    if "ID_ProdClteSustitutivo" in df_cruce.columns:
        df_cruce["ID_ProdClteSustitutivo"] = df_cruce["ID_ProdClteSustitutivo"].fillna("")

    # Si quieres fechas en formato dd/mm/yyyy solo para visualizar/exportar
    columnas_fecha = [
        "FechaProduccionPalet",
        "FechaCaducidadCalculada",
        "FechaCaducidadSegunPorcentaje"
    ]

    for col in columnas_fecha:
        if col in df_cruce.columns:
            df_cruce[col] = pd.to_datetime(df_cruce[col], errors="coerce").dt.strftime("%d/%m/%Y")

    engine.dispose()
    engine_sqlite.dispose()

    # Limpieza de columnas técnicas
    df_cruce = df_cruce.drop(
    columns=["ID_ProdClteSustitutivo"],
    errors="ignore")

    #Normalizamos Palets
    df_cruce["Palets"] = pd.to_numeric(df_cruce["Palets"], errors="coerce").fillna(0)


    # =========================
    # 12) Normalizamos df_stock
    # =========================

    
    df_stock["Referencia"] = df_stock["Referencia"].astype(str).str.strip()

    df_stock["Caducidad"] = pd.to_datetime(df_stock["Caducidad"], format="%Y-%m-%d %H:%M:%S", errors="coerce")

    df_stock["Stock"] = pd.to_numeric(df_stock["Stock"], errors="coerce").fillna(0)

    #Creamos un stock virtual para ver lo que vamos a consumir:

    stock_virtual = df_stock.copy()

    # =========================
    # 13) Recorrer todos los pedidos y calcular fechas
    # =========================

    df_cruce["FechaPropuesta_MayorIgual"] = ""
    df_cruce["StockDisponible_MayorIgual"] = 0
    df_cruce["Resultado_MayorIgual"] = ""

    df_cruce["FechaPropuesta_Exacta"] = ""
    df_cruce["StockDisponible_Exacta"] = 0
    df_cruce["Resultado_Exacta"] = ""

    
    df_cruce["FechaPropuesta_Porcentaje"] = ""
    df_cruce["StockDisponible_Porcentaje"] = 0
    df_cruce["Resultado_Porcentaje"] = ""


    for idx, fila in df_cruce.iterrows():

        referencia = str(fila["Referencia"]).strip()

        cantidad = pd.to_numeric(
            fila["Palets"],
            errors="coerce"
        )

        if pd.isna(cantidad):
            cantidad = 0

        fecha_objetivo = pd.to_datetime(
            fila["FCP Mayor o igual"],
            dayfirst=True,
            errors="coerce"
        )

        fecha, stock, estado = consumir_stock(
            stock_virtual,
            referencia,
            fecha_objetivo,
            cantidad
        )

        df_cruce.loc[idx, "FechaPropuesta_MayorIgual"] = fecha
        df_cruce.loc[idx, "StockDisponible_MayorIgual"] = stock
        df_cruce.loc[idx, "Resultado_MayorIgual"] = estado

    for idx, fila in df_cruce.iterrows():

        referencia = str(fila["Referencia"]).strip()

        cantidad = pd.to_numeric(
            fila["Palets"],
            errors="coerce"
        )

        if pd.isna(cantidad):
            cantidad = 0

        fecha_objetivo = pd.to_datetime(
            fila["FCP Exactamente igual"],
            dayfirst=True,
            errors="coerce"
        )

        fecha, stock, estado = consumir_stock(
            stock_virtual,
            referencia,
            fecha_objetivo,
            cantidad
        )

        df_cruce.loc[idx, "FechaPropuesta_Exacta"] = fecha
        df_cruce.loc[idx, "StockDisponible_Exacta"] = stock
        df_cruce.loc[idx, "Resultado_Exacta"] = estado

    for idx, fila in df_cruce.iterrows():

        referencia = str(fila["Referencia"]).strip()

        cantidad = pd.to_numeric(
            fila["Palets"],
            errors="coerce"
        )

        if pd.isna(cantidad):
            cantidad = 0

        fecha_objetivo = pd.to_datetime(
            fila["FechaCaducidadSegunPorcentaje"],
            dayfirst=True,
            errors="coerce"
        )

        fecha, stock, estado = consumir_stock(
            stock_virtual,
            referencia,
            fecha_objetivo,
            cantidad
        )

        df_cruce.loc[idx, "FechaPropuesta_Porcentaje"] = fecha
        df_cruce.loc[idx, "StockDisponible_Porcentaje"] = stock
        df_cruce.loc[idx, "Resultado_Porcentaje"] = estado

    output_file = f"cruce_pedidos_{date}.xlsx"

    with pd.ExcelWriter(output_file, engine="xlsxwriter") as writer:
        df_cruce.to_excel(writer, index=False, sheet_name="Datos")


        workbook = writer.book
        worksheet = writer.sheets["Datos"]

        # ==========================
        # FORMATOS
        # ==========================

        formato_rotura = workbook.add_format({
            "bg_color": "#FF9999"
        })

        formato_borde_rojo = workbook.add_format({
            "border": 2,
            "border_color": "red"
        })

        formato_fecha_borde = workbook.add_format({
            "num_format": "dd/mm/yyyy",
            "border": 2,
            "border_color": "red"
        })

        # ==========================
        # POSICIÓN DE COLUMNAS
        # ==========================

        columnas = {
            col: idx
            for idx, col in enumerate(df_cruce.columns)
        }

        # ==========================
        # RECORRER FILAS
        # ==========================

        for idx, fila in df_cruce.iterrows():

            fila_excel = idx + 1  # fila 0 = cabecera

            # ==========================
            # ROTURAS
            # ==========================

            rotura = any([
                fila.get("Resultado_MayorIgual") == "Rotura!",
                fila.get("Resultado_Exacta") == "Rotura!",
                fila.get("Resultado_Porcentaje") == "Rotura!"
            ])

            if rotura:

                worksheet.set_row(
                    fila_excel,
                    None,
                    formato_rotura
                )

            # ==========================
            # FCP MAYOR O IGUAL
            # ==========================

            if (
                pd.notna(fila.get("FCP Mayor o igual"))
                and pd.notna(fila.get("FechaPropuesta_MayorIgual"))
                and str(fila["FCP Mayor o igual"])
                != str(fila["FechaPropuesta_MayorIgual"])
            ):

                col = columnas["FechaPropuesta_MayorIgual"]

                worksheet.write(
                    fila_excel,
                    col,
                    fila["FechaPropuesta_MayorIgual"],
                    formato_borde_rojo
                )

            # ==========================
            # FCP EXACTAMENTE IGUAL
            # ==========================

            if (
                pd.notna(fila.get("FCP Exactamente igual"))
                and pd.notna(fila.get("FechaPropuesta_Exacta"))
                and str(fila["FCP Exactamente igual"])
                != str(fila["FechaPropuesta_Exacta"])
            ):

                col = columnas["FechaPropuesta_Exacta"]

                worksheet.write(
                    fila_excel,
                    col,
                    fila["FechaPropuesta_Exacta"],
                    formato_fecha_borde
                )

            # ==========================
            # FCP SEGÚN % VIDA ÚTIL
            # ==========================

            if (
                pd.notna(fila.get("FechaCaducidadSegunPorcentaje"))
                and pd.notna(fila.get("FechaPropuesta_Porcentaje"))
                and str(fila["FechaCaducidadSegunPorcentaje"])
                != str(fila["FechaPropuesta_Porcentaje"])
            ):

                col = columnas["FechaPropuesta_Porcentaje"]

                worksheet.write(
                    fila_excel,
                    col,
                    fila["FechaPropuesta_Porcentaje"],
                    formato_borde_rojo
                )

        # ==========================
        # AUTOAJUSTAR ANCHOS
        # ==========================

        for col in df_cruce.columns:
            try:
                _ = df_cruce[col].fillna("").astype(str).str.len().max()
            except Exception as e:
                print(f"ERROR EN COLUMNA: {col}")
                print(e)

        for i, col in enumerate(df_cruce.columns):

            try:
                ancho_datos = (df_cruce[col]
                    .fillna("")
                    .astype(str)
                    .str.len()
                    .max()
                )

                ancho = max(len(str(col)), ancho_datos) + 2

            except Exception:
                ancho = len(str(col)) + 2

            worksheet.set_column(i, i, min(ancho, 50))


        


    # nombre_archivo = f"cruce_pedidos_{date}.csv"
    # df_cruce.to_csv(nombre_archivo, index=False, sep=";", encoding="utf-8-sig")

    print("OK ->", output_file)

    return df_cruce


if __name__ == "__main__":

    df_resultado = cruce_archivos(
        archivo_pedidos=r"C:\Users\jgmeras\OneDrive - GXO\Documents\Python Scripts\01. MAHOU\Stock\pedidos_20260707150357.csv",
        archivo_fcp=r"C:\Users\jgmeras\OneDrive - GXO\Documents\Python Scripts\01. MAHOU\Stock\parsed_edis_20260707150413.xlsx",
        archivo_stock=r"C:\Users\jgmeras\OneDrive - GXO\Documents\Python Scripts\01. MAHOU\Stock\vUbicacionesProducto_20260707150414.xlsx",
        almacen=almacen
    )

    