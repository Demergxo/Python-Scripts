from sqlalchemy import create_engine, text #type:ignore
import pandas as pd
from datetime import datetime

fecha_inicio = '2026-02-12'
fecha_fin = '2026-02-14'
almacen = 129

def ejecutar_qry(fecha_inicio, fecha_fin, almacen):

    date = datetime.now().strftime("%Y%m%d%H%M%S")
    ddbb_name = "vUbicacionesProducto"


    def hora():
        hora = datetime.now().strftime("%H:%M:%S")
        return hora

    print(f"Hora de inicio: {hora()}")

    # --- CONEXIÓN SQLALCHEMY ---

    engine = create_engine("mssql+pyodbc://@XGA_PROD")

    # --- QUERY SQL (rango de fechas) ---
    query = text(f"""
        SELECT
            CodigoProdClte AS Referencia,
            NombreProdClte AS Descripción,
            CaducidadPalet AS Caducidad,
            SUM(CantidadActualPalet) AS Stock       
            
        FROM
            {ddbb_name}
    
        WHERE 
            
            ID_Cliente = 944   
            AND ID_Almacen = :almacen
            AND CodigoDeposito = '000'
            AND ZonaUbicacion NOT IN ('88', 'IN', 'PE', '99', '77')
            AND CodigoEstadoProd = 'B'

        
        GROUP BY
            CodigoProdClte,
            NombreProdClte,
            CaducidadPalet
        ORDER BY
            CodigoProdClte,
            CaducidadPalet

        
    """)
    # AND CONVERT(date, FechaProcesoDoc) BETWEEN CONVERT(date, :inicio) AND CONVERT(date, :fin)

    # --- EJECUTAR CONSULTA ---
    with engine.connect() as conn:
        df = pd.read_sql(query, conn, params={"inicio": fecha_inicio, "fin": fecha_fin, "almacen": almacen} )

    # --- EXPORTAR ---
    nombre_archivo = f"{ddbb_name}_{date}.xlsx"
    df.to_excel(nombre_archivo, index=False)

    print(f"✅ Archivo generado correctamente: {nombre_archivo}")

    print(f"Hora de fin: {hora()}")
    engine.dispose()
    return nombre_archivo


if __name__ == "__main__":
    ejecutar_qry(fecha_inicio, fecha_fin, almacen)
    
