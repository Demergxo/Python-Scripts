-- Query Cancelaciones --
-- Id, Fecha, Cantidad, Referencia, Responsabilidad (GXO / MSM), Seccion (IB / OB)


SELECT
    AlbaranDoc AS 'Albaran', CodigoPostal, NombreIncidenciaLinea,ID_TipoImputacion AS 'TipoImputacion', 
    PesoFiege AS 'PesoTeorico', PesoDespachado, PesoServido, VolumenFiege AS 'VolumenTeorico', LineasTeoricas, LineasIncidencia,
    PesoClienteDoc AS 'PesoCliente', VolumenClienteDoc AS 'VolumenCliente', FechaProcesoDoc AS 'Fecha', NombreTipoIncidencia
FROM
    vCapturasEstadisticasAnalitica
WHERE
    ID_Cliente = 944
    AND CONVERT(date, FechaProceso) BETWEEN CONVERT(date, :inicio) AND CONVERT(date, :fin)

------------------------------------------------------------------------------------------------------------------------------------------------------------------------

-- Query Entradas --
-- Id, Fecha, Kilos, CantidadRechazada, SSCCPalet
-- FALTA PESO --

    SELECT
         EntradaPalet AS 'Fecha', CantidadRechazada, SSCCPalet, CantidadTeorica, AlbaranDoc AS 'Albaran'
    FROM
        vAlbaranesRecepcionar
    WHERE
        ID_Cliente = 944
        AND CONVERT(date, EntradaPalet) BETWEEN CONVERT(date, :inicio) AND CONVERT(date, :fin)

---------------------------------------------------------------------------------------------------------------------------------------------------------------------

-- Query Recogidas --
-- Id, Fecha, Referencia, Kilos, UnidadesPallet
-- Verificar fecha --

    SELECT 
        FechaProgramadaDoc AS 'Fecha', PesoFiege AS 'Kilos', BultosFiege AS 'UnidadesPallet', AlbaranDoc AS 'Albaran', ID_Usuario AS 'Login', NombreUsuario AS 'Usuario'

    FROM
        vDocumentos
    WHERE 
        ID_Cliente = 944
        AND NombreTipoDocumento = 'Recogida'
        AND CONVERT(date, FechaProgramadaDoc) BETWEEN CONVERT(date, :inicio) AND CONVERT(date, :fin)
        
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------

-- Query Roturas / Ajustes --


    SELECT
        ID_Doc, FechaProcesoDoc AS 'Fecha', CodigoTipoAjuste, BultosFiege AS 'Cantidad', NombreUsuario AS 'Usuario', AlbaranDoc AS 'Albaran', ID_Usuario AS 'Login'

    FROM
        vDocumentos
     WHERE
        ID_Cliente = 944
        AND CodigoTipoDocumento = 'AJU' OR CodigoTipoDocumento 'RG-HUE'
        AND CONVERT(date, EntradaPalet) BETWEEN CONVERT(date, :inicio) AND CONVERT(date, :fin)   


--------------------------------------------------------------------------------------------------------------------------------------------------------------------------
-- Query Salidas


    SELECT
        AlbaranDoc AS 'Albaran', FechaProgramadaDoc AS 'Fecha', PesoFiege AS 'KilosTeoricos', VolumenFiege AS 'VolumenTeorico',
        BultosFiege AS 'PaletsTeoricos', PesoDespachado AS 'KilosDespachados', VolumenDespachado, BultosDespachado AS 'PaletsDespachados',
        ID_Usuario AS 'Login', NombreUsuario AS 'Usuario'

    FROM
        vDocumentos
     WHERE
        ID_Cliente = 944
        AND NombreTipoDocumento = 'Albaran'
        AND CONVERT(date, EntradaPalet) BETWEEN CONVERT(date, :inicio) AND CONVERT(date, :fin)   



--------------------------------------------------------------------------------------------------------------------------------------------------------------------------
-- Query Prod 



    SELECT
        FechaProcesoExtraccion AS 'Fecha', RTRIM(LoginUsuario) AS 'Usuario', PaletsEntradas, KilosEntradas, VolumenEntradas, MetrosRecorridosEnVacioEntradas,
        MetrosRecorridosOcupadoEntradas, PaletsSalidasPalets, KilosSalidasPalets, VolumenSalidasPalets, MetrosRecorridosEnVacioSalidasPalets, MetrosRecorridosOcupadoSalidasPalets,
        LineasSalidasPicking, KilosSalidasPicking, VolumenSalidasPicking, MetrosRecorridosEnVacioSalidasPicking, MetrosRecorridosOcupadoSalidasPicking, LineasSalidasPickingReclasificado,
        KilosSalidasPickingReclasificado, VolumenSalidasPickingReclasificado, MetrosRecorridosEnVacioPickingReclasificado, MetrosRecorridosOcupadoPickingReclasificado, PaletsReposicionPicking,
        KilosReposicionPicking, VolumenReposicionPicking, MetrosRecorridosEnVacioReposicionPicking, MetrosRecorridosOcupadoResposicionPicking, ProductividadEntradas,
        ProductividadPaletsSalida, ProductividadLineasSalidasPicking, ProductividadLineasSalidasPickingReclasificado, ProductividadPaletsReposicionPicking, CajasPicking,
        CajasPickingReclasificado, PaletsRecInterno, KilosPaletsRecInterno, VolumenRecorridoPalets, MetrosRecorridosEnVacioRecorridoInterno, MetrosRecorridosOcupadoInterno,
        ProductividadPaletsRecInterno

    FROM
        vRptEstadisticasManipulacion
     WHERE
        
        AND CONVERT(date, FechaProcesoExtraccion) BETWEEN CONVERT(date, :inicio) AND CONVERT(date, :fin)   

------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

