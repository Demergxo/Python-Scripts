from sqlalchemy import create_engine, text, bindparam
import pandas as pd
import time
import os

fecha_inicio = '2026-03-16'
fecha_fin = '2026-03-20'

path = os.getcwd()
DB_FILE = f"{path}\\apoyo.db"

def clean_str(df, col):
    if col in df.columns:
        df[col] = (
            df[col]
            .astype("string")
            .fillna("")
            .str.strip()
        )

def normalize_key(df, col):
    df[col] = (
        df[col]
        .astype("string")
        .fillna("")
        .str.strip()
    )

def consulta_pedidos(fecha_inicio, fecha_fin):
    date = time.strftime("%Y%m%d%H%M%S")

    # --- CONEXIÓN SQL SERVER ---
    engine = create_engine("mssql+pyodbc://@XGA_PROD")

    # --- QUERIES 1,2,3 ---
    q1 = text("""
        SELECT
            RTRIM(ID_Doc) AS ID_Doc,
            RTRIM(AlbaranDoc) AS Albarán,
            NombreDireccion AS [Razón Social],
            CampoCliente AS [Código Envio],
            NombreTipoDocumento AS [Tipo Documento]
        FROM vDocumentos
        WHERE
            ID_Cliente = 944
            AND ID_Almacen = 129
            AND CodigoDivisionCliente = '1084'
            AND CodigoTipoEstado IN ('000', '010', '020')
            AND (CodigoTipoDocumento = 'RS' OR CodigoTipoDocumento = 'ALB')
            AND CONVERT(date, FechaDoc) BETWEEN DATEADD(day, -7, CONVERT(date, :inicio))
                                           AND DATEADD(day,  7, CONVERT(date, :fin));
    """)

    q2 = text("""
        SELECT
            RTRIM(AlbaranDoc) AS Albarán,
            FechaTeoricaCargaDoc AS [Fecha de Carga]
        FROM Documentos
        WHERE
            ID_Cliente = 944
            AND ID_Almacen = 129
            AND ID_DivisionCliente = '1866'
            AND (ID_TipoDocumento = 1 OR ID_TipoDocumento = 3)
            AND CONVERT(date, FechaTeoricaCargaDoc) BETWEEN CONVERT(date, :inicio) AND CONVERT(date, :fin);
    """)

    q3 = text("""
        SELECT
            RTRIM(AlbaranDoc) AS Albarán,
            CodigoProdClte AS Referencia,
            NombreProdClte AS [Descripción],
            SUM(CantidadLinea) AS Palets
        FROM vLineasOrdenCompraAlbaranDoc
        WHERE
            ID_Cliente = 944
        GROUP BY
            RTRIM(AlbaranDoc), CodigoProdClte, NombreProdClte;
    """)

    with engine.connect() as conn:
        df1 = pd.read_sql(q1, conn, params={"inicio": fecha_inicio, "fin": fecha_fin})
        df2 = pd.read_sql(q2, conn, params={"inicio": fecha_inicio, "fin": fecha_fin})
        df3 = pd.read_sql(q3, conn)
    
        #df1.to_csv("df1.csv", index=False, sep=";", encoding="utf-8-sig")
        #df2.to_csv("df2.csv", index=False, sep=";", encoding="utf-8-sig")
        #df3.to_csv("df3.csv", index=False, sep=";", encoding="utf-8-sig")
    # --- NORMALIZACIÓN CLAVES ---
    for d in (df1, df2, df3):
        d["Albarán"] = d["Albarán"].astype(str).str.strip()

    df1["ID_Doc"] = df1["ID_Doc"].astype(str).str.strip()
    df1["Tipo Documento"] = df1["Tipo Documento"].astype(str).str.strip()

    
    df3["Descripción"] = df3["Descripción"].astype(str).str.strip()

    # --- MERGE 1+2 ---
    df_12 = df1.merge(df2, on="Albarán", how="left")
    # df_12.to_csv("df_12.csv", index=False, sep=";", encoding="utf-8-sig")

    # --- MERGE (1+2)+3 ---
    # Esto ya mantiene múltiples referencias por Albarán (1:N)
    df_123 = df_12.merge(df3, on="Albarán", how="left")
    #df_123.to_csv("df_123.csv", index=False, sep=";", encoding="utf-8-sig")

    # Tipos
    df_123["Palets"] = pd.to_numeric(df_123["Palets"], errors="coerce")

    # IDs de ALB (si no hay, no dispares query_4/5)
    ids_alb = (
        df_123.loc[df_123["Tipo Documento"].eq("Albaran"), "ID_Doc"]
        .dropna()
        .astype(str)
        .unique()
        .tolist()
    )

    # --- CONEXIÓN SQLITE (maestro_msm) ---
    engine_sqlite = create_engine(f"sqlite:///{DB_FILE}")
    df_maestro = pd.read_sql("SELECT ID_ProdClte, CodigoProdClte FROM maestro_msm", engine_sqlite)

    df_maestro["ID_ProdClte"] = pd.to_numeric(df_maestro["ID_ProdClte"], errors="coerce").astype(str)
    df_maestro["CodigoProdClte"] = df_maestro["CodigoProdClte"].astype(str).str.strip()
    # df_maestro.to_csv("df_maestro.csv", index=False, sep=";", encoding="utf-8-sig")

    # ========== 1) df_123: añadimos ID_ProdClte a partir de Referencia ==========
    df_123["Referencia"] = df_123["Referencia"].astype(str).str.strip()
    df_123 = df_123.merge(
        df_maestro.rename(columns={"CodigoProdClte": "Referencia"}),
        on="Referencia",
        how="left"
    )
    
    # df_123.to_csv("df_123(2).csv", index=False, sep=";", encoding="utf-8-sig")

    # ========== 2) df4 y df5 ==========
    if not ids_alb:
        df_45 = pd.DataFrame(columns=["ID_Doc", "ID_ProdClte", "CantidadTeorica", "FCP"])
    else:
        q4 = (
            text("""
                SELECT
                    RTRIM(ID_Doc) AS ID_Doc,
                    CodigoProdClte AS Referencia,
                    NombreProdClte AS Descripción,
                    SUM(CantidadTeorica) AS CantidadTeorica
                FROM vDocumentoslineasConsulta
                WHERE ID_Cliente = 944
                AND ID_Doc IN :ids
                GROUP BY RTRIM(ID_Doc), CodigoProdClte, NombreProdClte
            """).bindparams(bindparam("ids", expanding=True))
        )

        q5 = (
            text("""
                SELECT
                    RTRIM(ID_Doc) AS ID_Doc,
                    CaducidadLineadoc AS FCP,
                    ID_ProdClte
                FROM vLineasDocumentos
                WHERE ID_Cliente = 944
                AND ID_Almacen = 129
                AND ID_Doc IN :ids
            """).bindparams(bindparam("ids", expanding=True))
        )

        with engine.connect() as conn:
            df4 = pd.read_sql(q4, conn, params={"ids": ids_alb}) #type: ignore
            df5 = pd.read_sql(q5, conn, params={"ids": ids_alb}) #type: ignore
        df4["Referencia"] = df4["Referencia"].astype(str).str.strip()
        df5["ID_ProdClte"] = df5["ID_ProdClte"].astype(str).str.strip()
        # df4.to_csv("df4.csv", index=False, sep=";", encoding="utf-8-sig")
        # df5.to_csv("df5.csv", index=False, sep=";", encoding="utf-8-sig")
        #print("df4 ref unicas:", df4["Referencia"].nunique())
        #print("df_maestro ref unicas:", df_maestro["CodigoProdClte"].nunique())

        df4["ID_Doc"] = df4["ID_Doc"].astype(str).str.strip()
        df4["Referencia"] = df4["Referencia"].astype(str).fillna("").str.strip()
        df4["CantidadTeorica"] = pd.to_numeric(df4["CantidadTeorica"], errors="coerce")

        df5["ID_Doc"] = df5["ID_Doc"].astype(str).str.strip()
        df5["ID_ProdClte"] = df5["ID_ProdClte"].astype(str).fillna("").str.strip()
        df5["FCP"] = pd.to_datetime(df5["FCP"], errors="coerce")

        # --- df4: traducimos Referencia -> ID_ProdClte para poder unir por ID ---
        df4 = df4.merge(
            df_maestro.rename(columns={"CodigoProdClte": "Referencia"}),
            on="Referencia",
            how="left"
        )
        # df4 ahora tiene ID_ProdClte
        #df4.to_csv("df4(2).csv", index=False, sep=";", encoding="utf-8-sig")


        # --- Unimos df4 + df5 por (ID_Doc, ID_ProdClte) ---
        df_45 = df4.merge(
            df5,
            on=["ID_Doc", "ID_ProdClte"], how="left")

        df_45.to_csv("df_45.csv", index=False, sep=";", encoding="utf-8-sig")

    # --- NORMALIZACIÓN FINAL DE CLAVES ---
        
    for d in (df_123, df_45):
        normalize_key(d, "ID_Doc")
        normalize_key(d, "Referencia")


    # ========== 3) Merge final df_123 + df_45 por (ID_Doc, ID_ProdClte) ==========
    df_final = df_123.merge(
    df_45[["ID_Doc", "Referencia", "Descripción", "CantidadTeorica", "FCP"]],
    on=["ID_Doc", "Referencia"],
    how="outer",
    suffixes=("", "_q4"),
    #indicator=True
    )

    df_final["Referencia"] = df_final["Referencia"].fillna("")
    df_final["ID_ProdClte"] = df_final["ID_ProdClte"].fillna("").astype(str)
    df_final["Descripción"] = (df_final["Descripción"].fillna(df_final["Descripción_q4"]))


 # 1) Repetir Albarán para todas las líneas del mismo ID_Doc
    df_final["Albarán"] = (
    df_final
    .groupby("ID_Doc", dropna=False)["Albarán"]
    .ffill()
)
    cols_cabecera = [
    "Albarán",
    "Razón Social",
    "Código Envio",
    "Tipo Documento",
    "Fecha de Carga"
]

    df_final[cols_cabecera] = (
    df_final
    .groupby("ID_Doc", dropna=False)[cols_cabecera]
    .ffill()
)

    df_final = df_final[df_final["Referencia"].ne("")].copy()


  

    # Sustituir Palets por CantidadTeorica SOLO para Albaran si existe
    mask = df_final["Palets"].isna() & df_final["CantidadTeorica"].notna()
    df_final.loc[mask, "Palets"] = df_final.loc[mask, "CantidadTeorica"]

    df_final["Palets"] = pd.to_numeric(df_final["Palets"], errors="coerce").round(0).astype("Int64")

    # Limpieza de columnas técnicas
    df_final = df_final.drop(
    columns=["ID_Doc", "ID_ProdClte", "CantidadTeorica", "_merge", "Descripción_q4"],
    errors="ignore"
    )

    # --- EXPORT ---
    nombre_archivo = f"pedidos_{date}.csv"
    df_final.to_csv(nombre_archivo, index=False, sep=";", encoding="utf-8-sig")

    engine.dispose()
    print("OK ->", nombre_archivo)

if __name__ == "__main__":
    consulta_pedidos(fecha_inicio, fecha_fin)
