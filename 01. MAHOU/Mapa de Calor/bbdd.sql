ExtraccionesUltimoPick - NO
ExtraccionesPlanning (*) - NO
vExtraccionesCambioUbicacionAlbaran (*)
vExtraccionesDetalleAlbaran (*)
vInfExtSalDoc (*)
vRPTMovimientosProducto
vRPTMovimientosProductoNew



SELECT
        CONCAT(ZonaUbicacion, PasilloUbicacion, HuecoUbicacion, NivelUbicacion) AS Ubicacion, CodigoProdClte, COUNT(SSCCPalet)
    FROM
        vExtraccionesCambioUbicacionAlbaran
    WHERE    
        ID_Cliente = 944
        AND ID_Almacen = 129
        AND ID_Deposito = 258
        AND TipoMvtoPalet = 'S'
        AND CantidadMvtoPalet != 0
        AND CodigoProdClte NOT IN ('110', '186')
        AND ZonaUbicacion = 'MA'
        AND CodigoEstadoProd = 'B'
        AND ID_Extraccion != ''
    GROUP BY
        Ubicacion, CodigoProdClte