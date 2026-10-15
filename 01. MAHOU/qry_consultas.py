from sqlalchemy import create_engine, text #type:ignore
import pandas as pd
from datetime import datetime

date = datetime.now().strftime("%Y%m%d%H%M%S")
ddbb_name = "vRptEstadisticasManipulacion"

fecha_inicio = '2026-10-13'
fecha_fin = '2026-10-13'

def hora():
    hora = datetime.now().strftime("%H:%M:%S")
    return hora

print(f"[{hora()}] Inicio de ejecución") 

# --- CONEXIÓN SQLALCHEMY ---

engine = create_engine("mssql+pyodbc://@XGA_PROD")
print(f"[{hora()}] Conexión base de datos SQL")

# --- QUERY SQL (rango de fechas) ---
print(f"[{hora()}] Ejecución de Query {ddbb_name} con rango de fechas {fecha_inicio} - {fecha_fin}")
query = text(f"""
    SELECT
        *
    FROM
        {ddbb_name}
    WHERE
        ID_Cliente = 944
        AND ID_Almacen = 221
        AND CONVERT(date, FechaProcesoExtraccion) BETWEEN CONVERT(date, :inicio) AND CONVERT(date, :fin)        
   
""")

# WHERE
#         ID_Cliente = 944
#         AND ID_Almacen = 221
#         AND CONVERT(date, FechaProcesoDoc) BETWEEN CONVERT(date, :inicio) AND CONVERT(date, :fin)

query2 = text(f"""
    SELECT OBJECT_DEFINITION(OBJECT_ID('dbo.{ddbb_name}')) AS Definicion
""")


query_find = text("""
    SELECT
        DB_NAME() AS BaseDatosActual,
        s.name AS SchemaName,
        o.name AS ObjectName,
        o.type_desc,
        OBJECT_DEFINITION(o.object_id) AS Definicion
    FROM sys.objects o
    INNER JOIN sys.schemas s
        ON o.schema_id = s.schema_id
    WHERE o.name = 'vExpedienteConsultaExtraccion'
""")

query_def = text("""
    SELECT 
        m.definition
    FROM sys.sql_modules m
    INNER JOIN sys.objects o
        ON m.object_id = o.object_id
    INNER JOIN sys.schemas s
        ON o.schema_id = s.schema_id
    WHERE 
        s.name = 'dbo'
        AND o.name = 'vExpedienteConsultaExtraccion'
""")


query_permiso = text("""
    SELECT 
        HAS_PERMS_BY_NAME(
            'dbo.vExpedienteConsultaExtraccion',
            'OBJECT',
            'VIEW DEFINITION'
        ) AS TienePermisoViewDefinition
""")

query_consulta = text("""

        SELECT
    c.ORDINAL_POSITION,
    c.COLUMN_NAME,
    c.DATA_TYPE,
    c.CHARACTER_MAXIMUM_LENGTH,
    c.NUMERIC_PRECISION,
    c.NUMERIC_SCALE,
    c.IS_NULLABLE
FROM INFORMATION_SCHEMA.COLUMNS c
WHERE c.TABLE_NAME = 'ProductosClientes'
ORDER BY
    c.ORDINAL_POSITION
    """)

query_consulta2 = text("""

    SELECT
    COUNT(*) AS NumeroRegistros
FROM ProductosClientes
WHERE ID_Cliente = 944
""")

              
# SELECT
#     CONCAT(
#         COALESCE(ZonaUbicacion, ''),
#         '-', COALESCE(PasilloUbicacion, ''),
#         '-', COALESCE(HuecoUbicacion, ''),
#         '-', COALESCE(NivelUbicacion, '')
#     ) AS Ubicacion,
#     CodigoProdClte AS Referencia,
#     COUNT(SSCCPalet) AS Cantidad,
#     CAST(GETDATE() AS DATE) AS FechaConsulta
# FROM vExtraccionesCambioUbicacionAlbaran
# WHERE
#     ID_Cliente = 944
#     ID_Cliente = 950 (Kimberly Klark)
#     ID_Cliente = 847 (Hisense)  
#     AND ID_Almacen = 129 (Interim)
#     AND ID_Almacen = 221 (Steel)
#     AND ID_Almacen = 222 (Burgos)
#     ID_Cliente = 950 (Kimberly Klark)
#     AND ID_Deposito = 258
#     AND TipoMvtoPalet = 'S'
#     AND CantidadMvtoPalet <> 0
#     AND LTRIM(RTRIM(CodigoProdClte)) NOT IN ('110','186')
#     AND ZonaUbicacion IN ('MA', 'BA')
#     AND CodigoEstadoProd = 'B'
#     AND ID_Extraccion IS NOT NULL
#     AND LTRIM(RTRIM(ID_Extraccion)) <> ''
# GROUP BY
#     CONCAT(
#         COALESCE(ZonaUbicacion, ''),
#         '-', COALESCE(PasilloUbicacion, ''),
#         '-', COALESCE(HuecoUbicacion, ''),
#         '-', COALESCE(NivelUbicacion, '')
#     ),
# #     CodigoProdClte

#        WHERE
#         ID_Cliente = 944
#         AND ID_Almacen = 129
#         AND CONVERT(date, FechaDoc) BETWEEN CONVERT(date, :inicio) AND CONVERT(date, :fin)       
              
              
              
#               """)

 

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
    df = pd.read_sql(query_consulta2, conn, params={"inicio": fecha_inicio, "fin": fecha_fin} )
#print(df)

# --- EXPORTAR ---
nombre_archivo = f"consulta2_{date}.xlsx"
#nombre_archivo = f"{ddbb_name}_{date}.xlsx"
print(f"[{hora()}] Generación de archivo")
df.to_excel(nombre_archivo, index=False)

print(f"[{hora()}] ✅ Archivo generado correctamente: {nombre_archivo}")

print(f"[{hora()}] Fin de ejecución")
engine.dispose()



