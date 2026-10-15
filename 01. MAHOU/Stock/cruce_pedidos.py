import os
import time
import pandas as pd
from sqlalchemy import create_engine, text
from xlsxwriter.utility import xl_col_to_name


path = os.getcwd()
DB_FILE = os.path.join(path, "apoyo.db")
USER = os.getenv("USERNAME")

almacen = 221

def marcar_fila_borde_rojo(worksheet, fila_excel, ultima_columna, formato_linea_borde_rojo):
    worksheet.conditional_format(fila_excel, 0, fila_excel, ultima_columna,
                                 {"type": "formula", "criteria": "=TRUE",
                                  "format": formato_linea_borde_rojo})


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


def simular_pedidos(df_cruce, df_stock, df_maestro):
    """Reserva solo coberturas completas, en orden de pedidos, con stock compartido.

    PL: una unidad contiene CajasPaletProdClte cajas. CJ: una unidad es una caja.
    Las propuestas para una FCP exacta distinta no reservan ni validan stock.
    """
    maestro = df_maestro.drop_duplicates("Referencia").set_index("Referencia")
    id_ref = df_maestro.set_index("ID_ProdClte")["Referencia"].to_dict()
    relaciones = {}
    for _, producto in df_maestro.iterrows():
        ref = producto["Referencia"]
        alt = id_ref.get(producto["ID_ProdClteSustitutivo"])
        if alt and alt != ref:
            relaciones.setdefault(ref, []).append(("Directa", alt))
            relaciones.setdefault(alt, []).append(("Inversa", ref))

    def factor(ref):
        if ref not in maestro.index:
            return None
        prod = maestro.loc[ref]
        unidad = str(prod["CodigoUnidad"]).strip().upper()
        if unidad == "CJ":
            return 1.0
        valor = pd.to_numeric(prod["CajasPaletProdClte"], errors="coerce")
        if unidad == "PL" and pd.notna(valor) and valor > 0:
            return float(valor)
        return None

    virtual = df_stock.copy()
    virtual["Stock"] = virtual["Stock"].astype(float)
    resultado = df_cruce.copy()
    fechas = ["FechaPropuesta_Final", "FCP_SustitutivaDisponible"]
    numericas = ["StockDisponible_Final", "StockUnidades_Sustitutiva",
                 "CajasAportadas_Sustitutiva", "CajasPorUnidad_Sustitutiva",
                 "CajasNecesarias", "CajasDisponibles", "CajasFaltantes"]
    textos = ["CriterioAplicado", "Resultado_Final", "ReferenciaSustitutivaUsada",
              "TipoReferenciaSustitutiva", "Resultado_Sustitutiva", "DetalleCobertura",
              "MotivoRotura", "AvisoConversion", "Observaciones"]
    for col in fechas:
        resultado[col] = pd.NaT
    for col in numericas:
        resultado[col] = 0.0
    for col in textos:
        resultado[col] = ""
    for sufijo in ["Exacta", "MayorIgual", "Porcentaje", "SinFCP"]:
        resultado["FechaPropuesta_" + sufijo] = pd.NaT
        resultado["StockDisponible_" + sufijo] = 0.0
        resultado["Resultado_" + sufijo] = ""

    for idx, fila in resultado.iterrows():
        ref = fila["Referencia"]
        cantidad = fila["Palets"]
        if cantidad <= 0:
            continue
        porcentaje_original = fila.get("FCP según % vida útil", "")
        porcentaje_informado = pd.notna(porcentaje_original) and str(porcentaje_original).strip() not in ("", "nan", "None")
        if (pd.isna(fila["FCP Exactamente igual"]) and pd.isna(fila["FCP Mayor o igual"])
                and porcentaje_informado and pd.isna(fila["FechaCaducidadSegunPorcentaje"])):
            resultado.loc[idx, "Resultado_Final"] = "Revisar FCP"
            resultado.loc[idx, "CriterioAplicado"] = "FCP según % vida útil"
            resultado.loc[idx, "MotivoRotura"] = "No se puede calcular la FCP por porcentaje; revisar maestro/producción"
            resultado.loc[idx, "Observaciones"] = "No se puede proponer FCP sin calcular la condición solicitada. Revisar maestro/producción."
            continue
        if pd.notna(fila["FCP Exactamente igual"]):
            criterio, sufijo, fecha = "FCP Exactamente igual", "Exacta", fila["FCP Exactamente igual"]
        elif pd.notna(fila["FCP Mayor o igual"]):
            criterio, sufijo, fecha = "FCP Mayor o igual", "MayorIgual", fila["FCP Mayor o igual"]
        elif pd.notna(fila["FechaCaducidadSegunPorcentaje"]):
            criterio, sufijo, fecha = "FCP según % vida útil", "Porcentaje", fila["FechaCaducidadSegunPorcentaje"]
        else:
            criterio, sufijo, fecha = "Sin FCP - fecha más antigua", "SinFCP", pd.NaT
        resultado.loc[idx, "CriterioAplicado"] = criterio
        factor_pedido = factor(ref)
        # Si falta conversión, se puede comprobar el stock de la misma referencia
        # en su unidad original, pero nunca aceptar otra referencia por defecto.
        f_base = factor_pedido if factor_pedido is not None else 1.0
        necesarias = float(cantidad) * f_base
        refs = [("Original", ref, f_base)]
        vistos = {ref}
        avisos = []
        for tipo, alt in relaciones.get(ref, []):
            if alt in vistos:
                continue
            vistos.add(alt)
            f_alt = factor(alt)
            if factor_pedido is None or f_alt is None:
                avisos.append(alt)
                continue
            refs.append((tipo, alt, f_alt))
        if avisos:
            resultado.loc[idx, "AvisoConversion"] = "No se puede convertir: " + ", ".join(avisos)

        def plan(fecha_filtro, exacta=False):
            disponibles = []
            for tipo, codigo, f in refs:
                candidatos = virtual[(virtual["Referencia"] == codigo) & (virtual["Stock"] > 0)]
                if pd.notna(fecha_filtro):
                    if exacta:
                        candidatos = candidatos[candidatos["Caducidad"] == fecha_filtro]
                    else:
                        candidatos = candidatos[candidatos["Caducidad"] >= fecha_filtro]
                for stock_idx, linea in candidatos.sort_values("Caducidad").iterrows():
                    disponibles.append((stock_idx, tipo, codigo, f, float(linea["Stock"]), linea["Caducidad"]))
            # Preferir la referencia original; FEFO dentro de cada referencia.
            total = sum(item[3] * item[4] for item in disponibles)
            pendiente = necesarias
            consumos = []
            for stock_idx, tipo, codigo, f, uds, cad in disponibles:
                cajas = min(uds * f, pendiente)
                if cajas > 0:
                    consumos.append((stock_idx, tipo, codigo, f, cajas / f, cad))
                    pendiente -= cajas
                if pendiente <= 1e-9:
                    break
            return total, consumos

        total, consumos = plan(fecha, sufijo == "Exacta")
        estado = "OK" if total + 1e-9 >= necesarias else "Rotura!"
        fecha_propuesta = consumos[0][5] if consumos else pd.NaT
        disponible_valido = total
        propuestas = []
        if estado == "Rotura!" and pd.notna(fecha):
            fechas_stock = virtual.loc[
                virtual["Referencia"].isin([r[1] for r in refs]) & (virtual["Stock"] > 0),
                "Caducidad"
            ].dropna().unique()
            # Exacta: proponer fechas posteriores, una fecha por propuesta.
            # Mínima/porcentaje: proponer relajar el límite, empezando por el más cercano.
            if sufijo == "Exacta":
                fechas_alt = sorted(f for f in fechas_stock if f > fecha)
            else:
                fechas_alt = sorted((f for f in fechas_stock if f < fecha), reverse=True)
            for candidata in fechas_alt:
                candidata = pd.Timestamp(candidata)
                total_alt, consumos_alt = plan(candidata, sufijo == "Exacta")
                completa = total_alt + 1e-9 >= necesarias
                prefijo = "FCP " if sufijo == "Exacta" else "FCP desde "
                unidad_total = "cajas" if factor_pedido is not None else "unidades de la referencia"
                detalle_alt = []
                for _, _, codigo, f, uds, cad in consumos_alt:
                    unidad = str(maestro.loc[codigo, "CodigoUnidad"]).strip() if codigo in maestro.index else "unidad"
                    detalle_alt.append(f"{codigo}: {uds:g} {unidad} (FCP {cad:%d/%m/%Y})")
                propuestas.append(
                    f"{prefijo}{candidata:%d/%m/%Y}: {total_alt:g} {unidad_total} disponibles; "
                    + ("cubre el 100%" if completa else f"no cubre el 100%, faltan {necesarias-total_alt:g} {unidad_total}")
                    + " [" + "; ".join(detalle_alt) + "]"
                )
                if completa and estado != "Pendiente aceptación":
                    estado = "Pendiente aceptación"
                    total, consumos = total_alt, consumos_alt
                    fecha_propuesta = candidata

        if estado == "OK":
            for stock_idx, _, _, _, uds, _ in consumos:
                virtual.loc[stock_idx, "Stock"] = max(0.0, virtual.loc[stock_idx, "Stock"] - uds)
        elif estado == "Pendiente aceptación":
            resultado.loc[idx, "MotivoRotura"] = "FCP solicitada no cubierta; fecha propuesta pendiente de aceptación"
        else:
            resultado.loc[idx, "MotivoRotura"] = "Stock insuficiente para cubrir el 100%" + (
                "; revisar conversión" if avisos else "")

        resultado.loc[idx, "Resultado_Final"] = estado
        resultado.loc[idx, "FechaPropuesta_Final"] = fecha_propuesta
        resultado.loc[idx, "StockDisponible_Final"] = total / f_base
        resultado.loc[idx, "FechaPropuesta_" + sufijo] = fecha_propuesta
        resultado.loc[idx, "StockDisponible_" + sufijo] = total / f_base
        resultado.loc[idx, "Resultado_" + sufijo] = estado
        if factor_pedido is not None:
            resultado.loc[idx, "CajasNecesarias"] = necesarias
            resultado.loc[idx, "CajasDisponibles"] = disponible_valido
            resultado.loc[idx, "CajasFaltantes"] = max(0.0, necesarias - disponible_valido)
        detalle = []
        alternativas = []
        tipos = []
        for _, tipo, codigo, f, uds, cad in consumos:
            unidad = str(maestro.loc[codigo, "CodigoUnidad"]).strip() if codigo in maestro.index else "unidad"
            fecha_txt = cad.strftime("%d/%m/%Y") if pd.notna(cad) else "sin fecha"
            detalle.append(f"{codigo}: {uds:g} {unidad} ({fecha_txt})")
            if tipo != "Original":
                alternativas.append(codigo)
                tipos.append(tipo)
                resultado.loc[idx, "CajasAportadas_Sustitutiva"] += uds * f
                if len(set(alternativas)) == 1:
                    resultado.loc[idx, "CajasPorUnidad_Sustitutiva"] = f
                    resultado.loc[idx, "StockUnidades_Sustitutiva"] += uds
                    resultado.loc[idx, "FCP_SustitutivaDisponible"] = cad
        if len(set(alternativas)) > 1:
            resultado.loc[idx, "StockUnidades_Sustitutiva"] = 0.0
            resultado.loc[idx, "CajasPorUnidad_Sustitutiva"] = 0.0
        resultado.loc[idx, "DetalleCobertura"] = ("Disponible: " if estado == "Rotura!" else
                                                   "Propuesta: " if estado == "Pendiente aceptación" else
                                                   "Reservado: ") + "; ".join(detalle)
        if alternativas:
            resultado.loc[idx, "ReferenciaSustitutivaUsada"] = ", ".join(dict.fromkeys(alternativas))
            resultado.loc[idx, "TipoReferenciaSustitutiva"] = ", ".join(dict.fromkeys(tipos))
            resultado.loc[idx, "Resultado_Sustitutiva"] = estado
        if estado == "OK" and alternativas:
            resultado.loc[idx, "Observaciones"] = (
                "Cubierto al 100% con referencia alternativa y cumpliendo la FCP solicitada. "
                + "; ".join(detalle)
            )
        elif estado != "OK":
            if propuestas:
                resultado.loc[idx, "Observaciones"] = (
                    "No se cumple la FCP solicitada. Alternativas SIN reservar, requieren aceptación: "
                    + " | ".join(propuestas)
                )
            else:
                resultado.loc[idx, "Observaciones"] = (
                    "No hay una FCP alternativa con stock conocido para proponer. "
                    + resultado.loc[idx, "DetalleCobertura"]
                )
        if avisos:
            resultado.loc[idx, "Observaciones"] += " Revisar conversión de: " + ", ".join(avisos)
    return resultado


def preparar_hoja_supervisores(df_export, almacen):
    """Incluye incidencias y avisos, también cuando el pedido sí está cubierto."""
    datos = df_export.copy()
    def columna(nombre):
        return datos.get(nombre, pd.Series("", index=datos.index)).fillna("")

    estado = columna("Resultado_Final").astype(str).str.strip()
    motivo = columna("MotivoRotura").astype(str).str.strip()
    aviso = columna("AvisoConversion").astype(str).str.strip()
    incidencia_real = ((estado.ne("") & estado.ne("OK")) | motivo.ne("") | aviso.ne(""))
    cobertura_alternativa = estado.eq("OK") & columna("ReferenciaSustitutivaUsada").astype(str).str.strip().ne("")
    mascara = incidencia_real | cobertura_alternativa
    tipo_fila = pd.Series("Información de cobertura", index=datos.index).where(~incidencia_real, "Incidencia / aviso")
    incidencia = motivo.copy()
    incidencia = incidencia.where(incidencia.ne(""), estado.where(estado.ne("OK"), ""))
    incidencia = incidencia + ("; " + aviso).where(incidencia.ne("") & aviso.ne(""), aviso)

    criterio = columna("CriterioAplicado")
    fecha_solicitada = pd.Series("", index=datos.index)
    for texto, origen in [
        ("FCP Exactamente igual", "FCP Exactamente igual"),
        ("FCP Mayor o igual", "FCP Mayor o igual"),
        ("FCP según % vida útil", "FechaCaducidadSegunPorcentaje")
    ]:
        mask = criterio.eq(texto)
        fecha_solicitada.loc[mask] = columna(origen).loc[mask]

    # Cuando no hay conversión válida, los ceros iniciales no representan cajas.
    cajas_calculadas = pd.to_numeric(columna("CajasNecesarias"), errors="coerce").gt(0)
    salida = pd.DataFrame({
        "FECHA CARGA": columna("Fecha de Carga"),
        "ALMACEN": {221: "Steel", 129: "GXO Alovera1"}.get(almacen, str(almacen)),
        "Nº PEDIDO": columna("Albarán"),
        "RAZÓN SOCIAL": columna("Razón Social"),
        "REF": columna("Referencia"),
        "DESCRIPCIÓN": columna("Descripción"),
        "CANTIDAD": columna("Palets"),
        "UNIDAD": columna("CodigoUnidad").astype(str).str.strip(),
        "TIPO": tipo_fila,
        "ESTADO": estado,
        "INCIDENCIA": incidencia,
        "OBSERVACIONES": columna("Observaciones"),
        "CONDICIÓN FCP": criterio,
        "FCP SOLICITADA": fecha_solicitada,
        "% VIDA ÚTIL SOLICITADO": columna("FCP según % vida útil"),
        "FCP PROPUESTA": columna("FechaPropuesta_Final"),
        "CAJAS NECESARIAS": columna("CajasNecesarias").where(cajas_calculadas, ""),
        "CAJAS DISPONIBLES FCP SOLICITADA": columna("CajasDisponibles").where(cajas_calculadas, ""),
        "CAJAS FALTANTES FCP SOLICITADA": columna("CajasFaltantes").where(cajas_calculadas, ""),
        "REFERENCIAS ALTERNATIVAS": columna("ReferenciaSustitutivaUsada"),
        "DETALLE STOCK / PROPUESTA": columna("DetalleCobertura"),
        "AVISO CONVERSIÓN": aviso
    })
    return salida.loc[mascara].reset_index(drop=True)


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
            ID_ProdClteSustitutivo,
            CajasPaletProdClte
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

    df_maestro["CajasPaletProdClte"] = pd.to_numeric(df_maestro["CajasPaletProdClte"], errors="coerce")



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
            "FechaProduccionPalet",
            "FechaCaducidadCalculada",
            "DiasCaducidadProdClte",
            "CodigoUnidad",
            "ID_ProdClteSustitutivo",
            "ReferenciaSustitutiva"
        ]]
        .copy()
    )

    # =========================
    # 9) Cruzar df_cruce con maestro antiguo
    # =========================

    df_metadata = df_maestro.merge(df_sustitutivos, on="ID_ProdClteSustitutivo", how="left")
    df_metadata = df_metadata[["Referencia", "CodigoUnidad", "DiasCaducidadProdClte",
                               "ID_ProdClteSustitutivo", "ReferenciaSustitutiva"]].drop_duplicates("Referencia")
    df_fechas = df_maestro_antiguo[["Referencia", "FechaProduccionPalet", "FechaCaducidadCalculada"]]
    df_cruce = df_cruce.merge(df_metadata, on="Referencia", how="left", validate="m:1")
    df_cruce = df_cruce.merge(df_fechas, on="Referencia", how="left", validate="m:1")
    df_cruce = df_cruce.merge(df_sustitutivos_inverso, on="Referencia", how="left", validate="m:1")
    df_cruce["ReferenciaSustitutiva"] = df_cruce["ReferenciaSustitutiva"].fillna("")
    df_cruce["ReferenciaSustitutivaInversa"] = df_cruce["ReferenciaSustitutivaInversa"].fillna("")
    df_cruce["DiasCaducidadProdClte"] = pd.to_numeric(df_cruce["DiasCaducidadProdClte"], errors="coerce")

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

    df_cruce = simular_pedidos(df_cruce, df_stock, df_maestro)
    columnas_fecha_export = [
        "FCP Mayor o igual", "FCP Exactamente igual", "FechaProduccionPalet",
        "FechaCaducidadCalculada", "FechaCaducidadSegunPorcentaje",
        "FechaPropuesta_MayorIgual", "FechaPropuesta_Exacta",
        "FechaPropuesta_Porcentaje", "FechaPropuesta_SinFCP",
        "FechaPropuesta_Final", "FCP_SustitutivaDisponible"
    ]

    # =========================
    # 20) Crear df_export para ordenar y exportar
    # =========================

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

        # Se mantiene el nombre Faltas, pero recoge todas las incidencias y avisos.
        df_faltas_salida = preparar_hoja_supervisores(df_export, almacen)

        # =========================
        # Escribir hojas
        # =========================

        df_export.to_excel(
            writer,
            index=False,
            sheet_name="Datos"
        )

        df_faltas_salida.to_excel(
            writer,
            index=False,
            sheet_name="Faltas"
        )

        workbook = writer.book
        worksheet_datos = writer.sheets["Datos"]
        worksheet_faltas = writer.sheets["Faltas"]

        # ==========================
        # FORMATOS
        # ==========================

        formato_rotura = workbook.add_format({
            "bg_color": "#FF9999"
        })

        formato_linea_borde_rojo = workbook.add_format({
            "top": 2,
            "bottom": 2,
            "left": 2,
            "right": 2,
            "top_color": "red",
            "bottom_color": "red",
            "left_color": "red",
            "right_color": "red"
        })

        formato_cabecera_faltas = workbook.add_format({
            "bold": True,
            "bg_color": "#1F4E78",
            "font_color": "white",
            "border": 1
        })

        # ==========================
        # FORMATO HOJA DATOS
        # ==========================

        columnas = {
            col: idx
            for idx, col in enumerate(df_export.columns)
        }

        ultima_fila = len(df_export)
        ultima_columna = len(df_export.columns) - 1

        # ==========================
        # Fila completa roja si hay Rotura!
        # ==========================

        if "Resultado_Final" in columnas:

            col_idx = columnas["Resultado_Final"]
            col_excel = xl_col_to_name(col_idx)

            worksheet_datos.conditional_format(
                1,
                0,
                ultima_fila,
                ultima_columna,
                {
                    "type": "formula",
                    "criteria": f'=OR(${col_excel}2="Rotura!",${col_excel}2="Pendiente aceptación",${col_excel}2="Revisar FCP")',
                    "format": formato_rotura
                }
            )

        # ==========================
        # Bordes rojos en Datos solo si:
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

            # FCP Mayor o igual
            if criterio == "FCP Mayor o igual":

                fcp_cliente = fila.get("FCP Mayor o igual", "")
                fecha_propuesta = fila.get("FechaPropuesta_MayorIgual", "")

                if (
                    valor_valido_excel(fcp_cliente)
                    and valor_valido_excel(fecha_propuesta)
                    and str(fcp_cliente).strip() != str(fecha_propuesta).strip()
                ):
                    marcar_borde = True

            # FCP Exactamente igual
            elif criterio == "FCP Exactamente igual":

                fcp_cliente = fila.get("FCP Exactamente igual", "")
                fecha_propuesta = fila.get("FechaPropuesta_Exacta", "")

                if (
                    valor_valido_excel(fcp_cliente)
                    and valor_valido_excel(fecha_propuesta)
                    and str(fcp_cliente).strip() != str(fecha_propuesta).strip()
                ):
                    marcar_borde = True

            # FCP según % vida útil
            elif criterio == "FCP según % vida útil":

                fcp_calculada = fila.get("FechaCaducidadSegunPorcentaje", "")
                fecha_propuesta = fila.get("FechaPropuesta_Porcentaje", "")

                if (
                    valor_valido_excel(fcp_calculada)
                    and valor_valido_excel(fecha_propuesta)
                    and str(fcp_calculada).strip() != str(fecha_propuesta).strip()
                ):
                    marcar_borde = True

            # Sin FCP no se marca borde rojo
            if marcar_borde:
                marcar_fila_borde_rojo(
                    worksheet_datos,
                    fila_excel,
                    ultima_columna,
                    formato_linea_borde_rojo
                )

        # ==========================
        # Autoajustar columnas Datos
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

            worksheet_datos.set_column(i, i, min(ancho, 50))

        # ==========================
        # FORMATO HOJA FALTAS
        # ==========================

        for col_num, value in enumerate(df_faltas_salida.columns):
            worksheet_faltas.write(
                0,
                col_num,
                value,
                formato_cabecera_faltas
            )

        worksheet_faltas.freeze_panes(1, 0)
        if not df_faltas_salida.empty:
            worksheet_faltas.autofilter(0, 0, len(df_faltas_salida), len(df_faltas_salida.columns) - 1)
        formato_texto = workbook.add_format({"text_wrap": True, "valign": "top"})
        formato_aviso = workbook.add_format({"bg_color": "#FFF2CC"})
        formato_info = workbook.add_format({"bg_color": "#DDEBF7"})
        col_estado = xl_col_to_name(df_faltas_salida.columns.get_loc("ESTADO"))
        if not df_faltas_salida.empty:
            worksheet_faltas.conditional_format(1, 0, len(df_faltas_salida), len(df_faltas_salida.columns) - 1,
                {"type": "formula", "criteria": f'=${col_estado}2="Rotura!"', "format": formato_rotura})
            worksheet_faltas.conditional_format(1, 0, len(df_faltas_salida), len(df_faltas_salida.columns) - 1,
                {"type": "formula", "criteria": f'=AND(${col_estado}2<>"Rotura!",$I2="Incidencia / aviso")', "format": formato_aviso})
            worksheet_faltas.conditional_format(1, 0, len(df_faltas_salida), len(df_faltas_salida.columns) - 1,
                {"type": "formula", "criteria": '=$I2="Información de cobertura"', "format": formato_info})
        for fila in range(1, len(df_faltas_salida) + 1):
            texto = str(df_faltas_salida.iloc[fila - 1]["OBSERVACIONES"])
            lineas = max(4, (len(texto) + 44) // 45)
            worksheet_faltas.set_row(fila, min(409, lineas * 15))

        for i, col in enumerate(df_faltas_salida.columns):

            try:
                ancho_datos = (
                    df_faltas_salida[col]
                    .fillna("")
                    .astype(str)
                    .str.len()
                    .max()
                )

                ancho = max(len(str(col)), ancho_datos) + 2

            except Exception:
                ancho = len(str(col)) + 2

            worksheet_faltas.set_column(i, i, min(ancho, 50), formato_texto)

    print("OK ->", output_file)

    return df_cruce


if __name__ == "__main__":

    df_resultado = cruce_archivos(
        archivo_pedidos=r"C:\Users\jgmeras\OneDrive - GXO\Documents\Python Scripts\01. MAHOU\Stock\pedidos_20260707150357.csv",
        archivo_fcp=r"C:\Users\jgmeras\OneDrive - GXO\Documents\Python Scripts\01. MAHOU\Stock\parsed_edis_20260707150413.xlsx",
        archivo_stock=r"C:\Users\jgmeras\OneDrive - GXO\Documents\Python Scripts\01. MAHOU\Stock\vUbicacionesProducto_20260707150414.xlsx",
        almacen=almacen
    )