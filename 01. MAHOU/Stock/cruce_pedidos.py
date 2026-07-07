import os
import pandas as pd
import openpyxl
from sqlalchemy import Null, create_engine, text, bindparam

path = os.getcwd()
DB_FILE = f"{path}\\apoyo.db"


almacen = 221

def cruce_archivos(archivo_pedidos, archivo_fcp, archivo_stock, almacen):

    engine = create_engine("mssql+pyodbc://@XGA_PROD")

    df_pedidos = pd.read_csv(archivo_pedidos, sep=';', encoding='utf-8-sig', dtype=str)

    df_fcp = pd.read_excel(archivo_fcp, engine='openpyxl', sheet_name="Datos", dtype=str)

    df_stock = pd.read_excel(archivo_stock, engine='openpyxl', sheet_name="Sheet1", dtype=str)

    # Limpiar espacios en los nombres de columnas
    df_pedidos.columns = df_pedidos.columns.str.strip()
    df_fcp.columns = df_fcp.columns.str.strip()
    df_stock.columns = df_stock.columns.str.strip()

    # Limpiar espacios en los campos clave
    df_pedidos["Albarán"] = df_pedidos["Albarán"].fillna("").astype(str).str.strip()
    df_pedidos["Referencia"] = df_pedidos["Referencia"].fillna("").astype(str).str.strip()

    df_fcp["Pedido"] = df_fcp["Pedido"].fillna("").astype(str).str.strip()
    df_fcp["Referencia"] = df_fcp["Referencia"].fillna("").astype(str).str.strip()

    # Columnas que queremos traer desde df_fcp
    columnas_fcp = [
        "Pedido",
        "Referencia",
        "FCP Mayor o igual",
        "FCP Exactamente igual",
        "FCP según % vida útil"
    ]

    # Cruce df_pedidos contra df_fcp
    df_cruce = df_pedidos.merge(
        df_fcp[columnas_fcp],
        left_on=["Albarán", "Referencia"],
        right_on=["Pedido", "Referencia"],
        how="left"
    )

    # Si no necesitas mantener la columna Pedido porque ya tienes Albarán
    df_cruce = df_cruce.drop(columns=["Pedido"], errors="ignore")

    #print(df_cruce.head(10))
    

    query_stock_prod = text(f"""
        SELECT
            RTRIM(CodigoProdClte) AS [Referencia], NombreProdClte, FechaProduccionPalet, SUM(CantidadActualPalet) AS Stock 
        FROM
            vPalets
        WHERE
            ID_Cliente = 944
            AND ID_Almacen = :almacen
            AND CantidadActualPalet > 0
            AND ID_EstadoProd = 1
        GROUP BY
                RTRIM(CodigoProdClte), NombreProdClte, FechaProduccionPalet
            
            
    """)

    with engine.connect() as conn:
            df1 = pd.read_sql(query_stock_prod, conn, params={"almacen": almacen})

    # --- CONEXIÓN SQLITE (maestro_msm) ---
    engine_sqlite = create_engine(f"sqlite:///{DB_FILE}")

    query_maestro = text(
         """
        SELECT
            ID_ProdClte, RTRIM(CodigoProdClte) AS Referencia, CodigoUnidad, DiasCaducidadProdClte, ID_ProdClteSustitutivo 
        FROM
            maestro_msm""")

    with engine_sqlite.connect() as conn:
        df_maestro = pd.read_sql(query_maestro, conn)

    
    # Limpieza nombres de columnas por seguridad
    df1.columns = df1.columns.str.strip()
    df_maestro.columns = df_maestro.columns.str.strip()

    #cambiar de float a string
    df_maestro["ID_ProdClte"] = pd.to_numeric(df_maestro["ID_ProdClte"], errors="coerce").astype("Int64").astype(str)
    df_maestro["ID_ProdClteSustitutivo"] = pd.to_numeric(df_maestro["ID_ProdClteSustitutivo"], errors="coerce").astype("Int64").astype(str)

    # Limpieza campo clave
    df1["Referencia"] = df1["Referencia"].fillna("").astype(str).str.strip()
    df_maestro["Referencia"] = df_maestro["Referencia"].fillna("").astype(str).str.strip()


    df_1maestro = df1.merge(
        df_maestro,
        on="Referencia",
        how="left"
    )

        # Normalizar columnas del maestro
    df_maestro["ID_ProdClte"] = pd.to_numeric(
        df_maestro["ID_ProdClte"],
        errors="coerce"
    ).astype("Int64").astype("string")

    df_maestro["Referencia"] = (
        df_maestro["Referencia"]
        .fillna("")
        .astype(str)
        .str.strip()
    )

    # Normalizar ID_ProdClteSustitutivo en df_1maestro
    df_1maestro["ID_ProdClteSustitutivo"] = pd.to_numeric(
        df_1maestro["ID_ProdClteSustitutivo"],
        errors="coerce"
    ).astype("Int64").astype("string")


    # Crear tabla de equivalencias desde el MAESTRO COMPLETO
    df_equiv_sustitutivos = (
        df_maestro[["ID_ProdClte", "Referencia"]]
        .dropna(subset=["ID_ProdClte"])
        .drop_duplicates(subset=["ID_ProdClte"])
        .rename(columns={
            "ID_ProdClte": "ID_ProdClteSustitutivo",
            "Referencia": "ReferenciaSustitutiva"
        })
    )


    # Cruzar para obtener la referencia real del sustituto
    df_1maestro = df_1maestro.merge(
        df_equiv_sustitutivos,
        on="ID_ProdClteSustitutivo",
        how="left"
    )

    # Asegurar tipos correctos
    df_1maestro["FechaProduccionPalet"] = pd.to_datetime(df_1maestro["FechaProduccionPalet"], errors="coerce")

    df_1maestro["DiasCaducidadProdClte"] = pd.to_numeric(df_1maestro["DiasCaducidadProdClte"], errors="coerce")

    df_1maestro["FechaCaducidadCalculada"] = (
        df_1maestro["FechaProduccionPalet"] +
        pd.to_timedelta(df_1maestro["DiasCaducidadProdClte"], unit="D")
    )

    df_1maestro["FechaCaducidadCalculada"] = pd.to_datetime(df_1maestro["FechaCaducidadCalculada"], errors="coerce")

    df_1maestro = df_1maestro.drop(
    columns=["ID_ProdClte", "ID_ProdClteSustitutivo"],
    errors="ignore"
    )

    #Normalizar
    df_1maestro["Referencia"] = (
        df_1maestro["Referencia"]
        .fillna("")
        .astype(str)
        .str.strip()
    )

    df_cruce["Referencia"] = (
        df_cruce["Referencia"]
        .fillna("")
        .astype(str)
        .str.strip()
    )

    #elegir producción más antigua
    df_maestro_antiguo = (
    df_1maestro
    .sort_values(["Referencia", "FechaProduccionPalet"])
    .drop_duplicates(subset=["Referencia"], keep="first")
    [[
        "Referencia",
        "FechaProduccionPalet",
        "FechaCaducidadCalculada",
        "DiasCaducidadProdClte"
    ]]
    .copy()
    )
    #cruzamos df_cruce con df_maestro_antiguo
    df_cruce = df_cruce.merge(
    df_maestro_antiguo,
    on="Referencia",
    how="left"
    )
    #normalizamos campo FCP %

    porcentaje = (
    df_cruce["FCP según % vida útil"]
    .astype(str)
    .str.replace("%", "", regex=False)
    .str.replace(",", ".", regex=False)
    .str.strip()
    )

    porcentaje = pd.to_numeric(porcentaje, errors="coerce")
    porcentaje = porcentaje.where(porcentaje <= 1, porcentaje / 100)

    #calculamos nueva fecha

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

    # Asegurar que los nombres de columnas no tienen espacios raros
    df_cruce.columns = df_cruce.columns.str.strip()
    df_maestro.columns = df_maestro.columns.str.strip()


    # Normalizar ID_ProdClteSustitutivo en df_cruce
    df_cruce["ID_ProdClteSustitutivo"] = pd.to_numeric(
        df_cruce["ID_ProdClteSustitutivo"],
        errors="coerce"
    ).astype("Int64").astype("string")


    # Normalizar ID_ProdClte en df_maestro
    df_maestro["ID_ProdClte"] = pd.to_numeric(
        df_maestro["ID_ProdClte"],
        errors="coerce"
    ).astype("Int64").astype("string")


    # Normalizar Referencia en df_maestro
    df_maestro["Referencia"] = (
        df_maestro["Referencia"]
        .fillna("")
        .astype(str)
        .str.strip()
    )


    # Crear tabla auxiliar: ID_ProdClte -> Referencia
    df_sustitutivos = (
        df_maestro[["ID_ProdClte", "Referencia"]]
        .dropna(subset=["ID_ProdClte"])
        .drop_duplicates(subset=["ID_ProdClte"])
        .rename(columns={
            "ID_ProdClte": "ID_ProdClteSustitutivo",
            "Referencia": "ReferenciaSustitutiva"
        })
    )


    # Cruzar contra df_cruce
    df_cruce = df_cruce.merge(
        df_sustitutivos,
        on="ID_ProdClteSustitutivo",
        how="left"
    )


    # Si no tiene ID_ProdClteSustitutivo o no encuentra referencia, dejar vacío
    df_cruce["ReferenciaSustitutiva"] = df_cruce["ReferenciaSustitutiva"].fillna("")    

    #print(df1.head(10))
    #print(df_maestro.head(10))
    #print(df_1maestro.head(10))
    # print("\n")
    # print("*"*50)
    # print("\n")
    #print(df_cruce.head(10))
    #print(df_stock.head(10))
    # nombre_archivo = f"pedidos_prueba.csv"
    # df_cruce.to_csv(nombre_archivo, index=False, sep=";", encoding="utf-8-sig")


    return df_cruce

if __name__ == "__main__":
    
    cruce_archivos(
        archivo_pedidos=r"C:\Users\jgmeras\OneDrive - GXO\Documents\Python Scripts\01. MAHOU\Stock\pedidos_20260707101221.csv",
        archivo_fcp=r"C:\Users\jgmeras\OneDrive - GXO\Documents\Python Scripts\01. MAHOU\Stock\parsed_edis_20260707101235.xlsx",
        archivo_stock=r"C:\Users\jgmeras\OneDrive - GXO\Documents\Python Scripts\01. MAHOU\Stock\vUbicacionesProducto_20260707101236.xlsx", 
        almacen=almacen   
    )