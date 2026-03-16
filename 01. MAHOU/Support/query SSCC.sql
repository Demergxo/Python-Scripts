    SELECT
        ID_Doc, AlbaranDoc AS 'Albarán', 
    FROM
        vDocumentos
    WHERE
        ID_Cliente = 944
        AND NombreTipoDocumento = 'Albaran'
        AND CONVERT(date, FechaDoc) BETWEEN CONVERT(date, :inicio) AND CONVERT(date, :fin)


    SELECT 
        ID_Doc, CodigoProdClte AS 'Referencia', NombreProdClte AS 'Descripción Producto', ID_UndExpedicion AS 'Unidades', SSCCPaletPicking AS 'SSCC'

    FROM
        vLineasDocumentosPreparadas
    WHERE 
        ID_Cliente = 944
        



