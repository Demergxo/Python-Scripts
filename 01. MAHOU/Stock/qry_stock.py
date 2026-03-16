from sqlalchemy import create_engine, text
import pandas as pd 
import time
import os

path = os.getcwd()

def consulta_stock():

    # --- CONFIGURACIÓN GENERAL ---
    date = time.strftime("%Y%m%d%H%M%S")

    # --- CONEXIÓN SQL SERVER ---
    engine = create_engine("mssql+pyodbc://@XGA_PROD")
    
    # --- QUERY SQL ---
    query = text("""
    SELECT
        CaducidadPalet AS 'FCP', ZonaUbicacion, PasilloUbicacion, HuecoUbicacion, NivelUbicacion, CodigoProdClte AS 'Referencia',
        NombreProdClte AS 'Descripción', DiasFechaProdClte AS 'Días Caducidad', SSCCPalet AS 'SSCC'
    FROM
        vUbicacionesProducto
    WHERE
        ID_Cliente = 944
        AND CodigoDeposito = '000'
    """)

    query_pend = text("""
    SELECT
        CodigoProdClte AS 'Referencia', NombreTipoAlmacenaje AS 'Medida',
        CajasPaletProdClte AS 'Cajas por Palet', NombreSector AS 'Grupo', NombreGrupo AS 'Tipologia'
    FROM
        vStocks
    WHERE
        ID_Cliente = 944
        AND ID_Almacen = 129
        AND CodigoDeposito = '000' 
        AND CodigoEstadoProd = 'B'

""")
    
    # --- EJECUTAR CONSULTA SQL SERVER ---
    with engine.connect() as conn:
        df_doc = pd.read_sql(query, conn)
        df_pend = pd.read_sql(query_pend, conn)

    df_doc["Ubicacion"] = (
    df_doc["ZonaUbicacion"].astype(str) + "-" +
    df_doc["PasilloUbicacion"].astype(str) + "-" +
    df_doc["HuecoUbicacion"].astype(str) + "-" +
    df_doc["NivelUbicacion"].astype(str)
)

    # Agrupar y sumar cantidad
    df_doc_agrupado = (
        df_doc
        .groupby(
            ["Ubicacion", "Referencia", "Descripción", "FCP"],
            as_index=False
        )
        .agg(
            Cantidad=("SSCC", "count")
        )
    )

    # Merge con stock
    df = df_doc_agrupado.merge(df_pend, on="Referencia", how="left")

    nombre_archivo = f"stock_{date}.csv"
    df.to_csv(nombre_archivo, index=False, sep=";", encoding='utf-8-sig')
    #print(f"✅ Archivo CSV generado correctamente: {nombre_archivo}")

    engine.dispose()
        


if __name__ == "__main__":
    consulta_stock()