SELECT 
        FechaProcesoDoc AS 'Fecha Expedición', FechaProgramadaDoc AS 'Fecha Requerida', ObsDocumento1 AS 'Horario Descarga', '' AS 'Instrucciones de entrega',
        '' AS 'Agrupación carga / Matrícula', '' AS 'Hora de Carga','' AS 'Tipo Doc', RTRIM(AlbaranDoc) AS 'Nº Documento', PedidoDestinatarioDoc AS 'Pedido Cliente'
        CodigoDireccion AS 'Cliente Envío', NombreDireccion AS 'Descripción Cliente Envío', , PoblacionDireccion AS 'Población',CodigoPostal AS 'Código Postal', 
        '' AS 'Direccio de entrega', ROUND(PesoFiege, 0) AS 'Peso Bruto', ROUND(BultosFiege, 0) AS 'Palés', '527' AS 'Estado', '' AS 'Peso Facturable (Real Taisa)',
        '' AS 'Palés Reales Taisa', '' AS 'Bases Reales Taisa', '8180' AS 'Almacén', '' AS 'Canal', '' AS 'Transporte'
    FROM
        vDocumentoConsulta 
    WHERE 
        ID_Cliente = 944
        AND NombreTipoDocumento = 'Albaran'
        AND CONVERT(date, FechaProcesoDoc) BETWEEN CONVERT(date, :inicio) AND CONVERT(date, :fin) 

   
-- Recuerda quitar 2 00 en CodigoDireccion
-- Cambiar formato de fecha a DD/MM/AAA




-- #################################################################################################################################################################
SELECT
    RTRIM(AlbaranDoc) AS AlbaranDoc, CampoCliente AS 'Tipo Doc', RTRIM(RutaReparto) AS RutaReparto
    FROM    
    vDocumentos
WHERE
    ID_Cliente = 944
    AND NombreTipoDocumento = 'Albaran'
    
