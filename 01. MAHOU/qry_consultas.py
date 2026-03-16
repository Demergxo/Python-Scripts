from sqlalchemy import create_engine, text #type:ignore
import pandas as pd
from datetime import datetime

date = datetime.now().strftime("%Y%m%d%H%M%S")
ddbb_name = "Usuarios"

fecha_inicio = '2026-03-02'
fecha_fin = '2026-03-10'

def hora():
    hora = datetime.now().strftime("%H:%M:%S")
    return hora

print(f"Hora de inicio: {hora()}")

# --- CONEXIÓN SQLALCHEMY ---

engine = create_engine("mssql+pyodbc://@XGA_PROD")

# --- QUERY SQL (rango de fechas) ---
query = text(f"""
    SELECT
        *
    FROM
        {ddbb_name}
    
       
                        
""")

query2 = text("""
              
              
SELECT
    CONCAT(
        COALESCE(ZonaUbicacion, ''),
        '-', COALESCE(PasilloUbicacion, ''),
        '-', COALESCE(HuecoUbicacion, ''),
        '-', COALESCE(NivelUbicacion, '')
    ) AS Ubicacion,
    CodigoProdClte AS Referencia,
    COUNT(SSCCPalet) AS Cantidad,
    CAST(GETDATE() AS DATE) AS FechaConsulta
FROM vExtraccionesCambioUbicacionAlbaran
WHERE
    ID_Cliente = 944
    AND ID_Almacen = 129
    AND ID_Deposito = 258
    AND TipoMvtoPalet = 'S'
    AND CantidadMvtoPalet <> 0
    AND LTRIM(RTRIM(CodigoProdClte)) NOT IN ('110','186')
    AND ZonaUbicacion IN ('MA', 'BA')
    AND CodigoEstadoProd = 'B'
    AND ID_Extraccion IS NOT NULL
    AND LTRIM(RTRIM(ID_Extraccion)) <> ''
GROUP BY
    CONCAT(
        COALESCE(ZonaUbicacion, ''),
        '-', COALESCE(PasilloUbicacion, ''),
        '-', COALESCE(HuecoUbicacion, ''),
        '-', COALESCE(NivelUbicacion, '')
    ),
    CodigoProdClte

              
              
              
              
              """)

 

 #AND CodigoAlmacen = 998
 #       AND CodigoDeposito = '000'
 #       AND CodigoTipoEstado IN ('000', '010', '020')
#AND CodigoDeposito = '000'
#        GROUP BY
#            RTRIM(ID_Doc), CodigoProdClte, NombreProdClte
#--AND CONVERT(date, FechaProgramadaDoc) BETWEEN CONVERT(date, :inicio) AND CONVERT(date, :fin);
        # AND PesoFiege = 0
        # AND CONVERT(date, FechaProcesoDoc) BETWEEN CONVERT(date, :inicio) AND CONVERT(date, :fin)
        # AND CodigoTipoDocumento IN ('REC', 'RS')
        # AND CodigoTipoEstado IN ('000', '010', '020')


#AND NombreTipoDocumento = 'Albaran' // RTRIM(AlbaranDoc) AS 'Albarán', FechaTeoricaCargaDoc AS 'Fecha de Carga'
# // TOP 30 // AlbaranDoc AS 'Albarán', NombreDireccion AS 'Razón Social', CampoCliente AS 'Código Envio', NombreTipoDocumento AS 'Tipo Documento' 
# vDocumentos   // RTRIM(AlbaranDoc) AS 'Albarán', ID_ProdClte AS 'Referencia', PaletsClienteDoc AS 'Palets'
#AND ID_Almacen = 129
#        AND CONVERT(date, FechaDoc) BETWEEN CONVERT(date, :inicio) AND CONVERT(date, :fin);
# AND CONVERT(date, FechaDoc) BETWEEN DATEADD(day, -7, CONVERT(date, :inicio)) AND DATEADD(day, 7, CONVERT(date, :fin));

#WHERE 
# #    CodigoCliente = 1084 // AND CONVERT(date, FechaProcesoDoc) BETWEEN DATEADD(day, -7,CONVERT(date, '2025-12-01')) AND DATEADD(day, 7, CONVERT(date, '2026-01-31'))
#      CodigoCliente = 100 
# WHERE 
#     ID_Cliente = 944
#     ID_Cliente = 24
#     ID_Almacen = 129     
#    AND CONVERT(date, FechaDoc) BETWEEN CONVERT(date, '2025-12-01') AND CONVERT(date, '2025-12-02')       
# WHERE
#     AlbaranDoc = '15352933'
# params={"inicio": fecha_inicio, "fin": fecha_fin}
#     AND NombreTipoDocumento = 'Albaran'
# AND
#     CONVERT(date, FechaProgramadaDoc) BETWEEN CONVERT(date, '2025-09-01') AND CONVERT(date, '2025-12-30')
# AND
#     CONVERT(date, FechaDoc) BETWEEN CONVERT(date, '2025-09-01') AND CONVERT(date, '2025-09-30')
#WHERE
# #        ID_Almacen = 129
#  AND ID_Almacen = 129
#         AND ID_Deposito = 258
#         AND TipoMvtoPalet = 'S'
#         AND CantidadMvtoPalet != 0
#         AND CodigoProdClte NOT IN ('110', '186')
#         AND ZonaUbicacion = 'MA'
#         AND CodigoEstadoProd = 'B'
#         AND ID_Extraccion != ''



# --- EJECUTAR CONSULTA ---
with engine.connect() as conn:
    df = pd.read_sql(query, conn, params={"inicio": fecha_inicio, "fin": fecha_fin} )

# --- EXPORTAR ---
nombre_archivo = f"{ddbb_name}_{date}.xlsx"
df.to_excel(nombre_archivo, index=False)

print(f"✅ Archivo generado correctamente: {nombre_archivo}")

print(f"Hora de fin: {hora()}")
engine.dispose()



