from sqlalchemy import create_engine, text
import pandas as pd 
import time
import os



def consulta_md():

    # --- CONFIGURACIÓN GENERAL ---
    date = time.strftime("%Y%m%d%H%M%S")

    # --- CONEXIÓN SQL SERVER ---
    engine = create_engine("mssql+pyodbc://@XGA_PROD")
    
    # --- QUERY SQL ---
    query = text("""
       SELECT
        CodigoProdClte AS 'Referencia', NombreProdClte AS 'Descripción', CajasPaletProdClte AS 'Cajas por Palet', BajaProdClte AS 'Activo', ID_Sector as 'Grupo',
        CapasPaletProdClte AS 'Capas', ID_ProdClte, ID_ProdClteSustitutivo  AS 'Sustitutivo', DiasCuarentenaProdClte AS 'Días Cuarentena',CodigoUnidad AS 'Tipo', 1 AS 'Unidad Palet'
    FROM    
        ProductosClientes
    WHERE
        ID_Cliente = 944
    
    """)

   
    # --- EJECUTAR CONSULTA SQL SERVER ---
    with engine.connect() as conn:
        df_doc = pd.read_sql(query, conn)
        
    df_doc["Activo"] = df_doc["Activo"].apply(
        lambda x: "SI" if pd.isna(x) or x == "" else "NO"
    )

    df_doc["Grupo"] = df_doc["Grupo"].map({
    91: "Cerveza",
    92: "Agua"
    }).fillna("Otros")

    id_to_referencia = (
    df_doc
    .set_index("ID_ProdClte")["Referencia"]
    .to_dict()
    )

    df_doc["Sustitutivo"] = (
    df_doc["Sustitutivo"]
    .map(id_to_referencia)
    .fillna("")
    )

    df_doc["Capas"] = df_doc["Capas"].round(0).astype("Int64")

    df_doc = df_doc.drop(columns=['ID_ProdClte'], errors='ignore')


    nombre_archivo = f"md_{date}.csv"
    df_doc.to_csv(nombre_archivo, index=False, sep=";", encoding='utf-8-sig')
    #print(f"✅ Archivo CSV generado correctamente: {nombre_archivo}")

    engine.dispose()
        


if __name__ == "__main__":
    consulta_md()