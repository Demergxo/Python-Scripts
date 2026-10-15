WITH DOCS_BASE AS
(
    SELECT
        ID_Cliente,
        ID_Doc,
        ID_Almacen,
        ID_DivisionCliente,
        ID_UltimoTipoEstado,
        ID_UltimoEstado,
        ID_RutaReparto,
        ID_ExpedienteDetalle,
        AlbaranDoc,
        FechaTeoricaCargaDoc,
        FechaProgramadaDoc,
        FechaTeoricaServicioDoc,
        ShipmentNumberDoc
    FROM Documentos WITH (NOLOCK)
    WHERE ID_Cliente = 944
      AND ID_Almacen = 221
      AND ID_UltimoTipoEstado IN (1,2,3,4)
      AND FechaTeoricaCargaDoc >= DATEADD(DAY, -7, GETDATE())
),
MP_S AS
(
    SELECT
        MP.ID_Cliente,
        MP.ID_Doc,
        MP.ID_Extraccion,
        MP.ID_PaletPicking,
        MP.ID_PaletPickingReclasificado,
        MP.CnfPreparacionCrossdockMvtoPalet,
        MP.confirmadoMvtoPalet
    FROM MovimientosPalets MP WITH (NOLOCK)
    INNER JOIN DOCS_BASE DB
        ON MP.ID_Cliente = DB.ID_Cliente
       AND MP.ID_Doc = DB.ID_Doc
    WHERE MP.TipoMvtoPalet = 'S'
),
TAB AS
(
    SELECT
        EP.ID_Cliente AS ID_Cliente,
        EP.ID_Doc AS ID_Doc,
        E.ID_Extraccion AS ID_Extraccion,
        E.ID_Expediente AS ID_Expediente,
        E.ID_UbicacionMuelle AS ID_UbicacionMuelle,
        MAX(EP.ID_UsuarioPreasignado) AS ID_UsuarioPreasignado,
        CASE
            WHEN SUM(CASE WHEN EP.BloqueadoExtrPlanning = 0 THEN 1 ELSE 0 END) = 0 THEN 1
            ELSE 0
        END AS Bloqueado,
        EP.ID_Deposito AS ID_Deposito,
        CASE
            WHEN SUM(CASE WHEN EP.ConfirmadoMovimiento = 0 THEN 1 ELSE 0 END) > 0
              OR SUM(CASE WHEN UPP.ID_TipoUbicacion IN (3,4) THEN 1 ELSE 0 END) > 0
              OR MAX(CAST(ISNULL(DC.CrearSoporteCargaDivisionCliente, 0) AS int)) = 1
              OR MAX(CAST(ISNULL(DC.PackingDivisionCliente, 0) AS int)) = 1
            THEN
                CASE
                    WHEN E.ID_UbicacionMuelle IS NULL THEN 1
                    ELSE
                        CASE
                            WHEN NOT EXISTS
                            (
                                SELECT 1
                                FROM MP_S MP
                                WHERE MP.ID_Extraccion = E.ID_Extraccion
                            ) THEN 2
                            WHEN MAX(CAST(ISNULL(DC.PackingDivisionCliente, 0) AS int)) = 1
                             AND E.ID_UbicacionMuelle IS NOT NULL
                             AND NOT EXISTS
                            (
                                SELECT 1
                                FROM MP_S MP
                                WHERE MP.ID_Extraccion = E.ID_Extraccion
                                  AND ISNULL(MP.CnfPreparacionCrossdockMvtoPalet, 0) <> ISNULL(MP.confirmadoMvtoPalet, 0)
                            ) THEN 5
                            WHEN MAX(CAST(ISNULL(DC.CrearSoporteCargaDivisionCliente, 0) AS int)) = 1
                             AND E.ID_UbicacionMuelle IS NOT NULL
                             AND NOT EXISTS
                            (
                                SELECT 1
                                FROM MP_S MP
                                WHERE MP.ID_Extraccion = E.ID_Extraccion
                                  AND MP.ID_PaletPickingReclasificado IS NULL
                            ) THEN 6
                            ELSE 2
                        END
                END
            ELSE 3
        END AS ID_TipoPrepExtr,
        SUM(CASE WHEN EP.EsPicking = 0 THEN 1 ELSE 0 END) AS PaletsCompletos,
        SUM(CASE WHEN EP.EsPicking = 0 AND EP.ConfirmadoMovimiento = 1 THEN 1 ELSE 0 END) AS PaletsCompletosLeidos,
        SUM(
            CASE
                WHEN EP.EsPicking = 0 THEN 1.0
                ELSE (EP.Cantidad * 1.0) / PROD.FactorPalets
            END
        ) AS TotalPalets,
        CEILING(
            SUM(
                CASE
                    WHEN EP.EsPicking = 0 THEN 1.0 / PROD.PaletsPorBase
                    ELSE 0
                END
            )
        ) AS PaletsBases,
        COUNT(DISTINCT PP.ID_PaletPicking) AS PaletsPickingBase,
        SUM(
            CASE
                WHEN EP.ConfirmadoMovimiento = 1 THEN
                    CASE
                        WHEN EP.EsPicking = 0 THEN 1.0
                        ELSE (EP.Cantidad * 1.0) / PROD.FactorPalets
                    END
                ELSE 0
            END
        ) AS TotalPaletsLeidos,
        SUM(CASE WHEN EP.EsPicking = 1 THEN EP.Cantidad / PROD.FactorCajas ELSE 0 END) AS PickingCajas,
        SUM(CASE WHEN EP.EsPicking = 1 AND EP.ConfirmadoMovimiento = 1 THEN EP.Cantidad / PROD.FactorCajas ELSE 0 END) AS PickingCajasLeidas,
        SUM(CASE WHEN EP.EsPicking = 1 THEN (EP.Cantidad % PROD.FactorCajas) / PROD.FactorEstuches ELSE 0 END) AS PickingEstuches,
        SUM(CASE WHEN EP.EsPicking = 1 AND EP.ConfirmadoMovimiento = 1 THEN (EP.Cantidad % PROD.FactorCajas) / PROD.FactorEstuches ELSE 0 END) AS PickingEstuchesLeidos,
        SUM(CASE WHEN EP.EsPicking = 1 THEN (EP.Cantidad % PROD.FactorCajas) % PROD.FactorEstuches ELSE 0 END) AS PickingUnidades,
        SUM(CASE WHEN EP.EsPicking = 1 AND EP.ConfirmadoMovimiento = 1 THEN (EP.Cantidad % PROD.FactorCajas) % PROD.FactorEstuches ELSE 0 END) AS PickingUnidadesLeidas,
        COUNT(*) AS Picks,
        SUM(CASE WHEN EP.ConfirmadoMovimiento = 1 THEN 1 ELSE 0 END) AS PicksLeidos,
        E.FechaUbicacionMuelle AS FechaUbicacionMuelle,
        ISNULL(EXP.HoraPrevistaLlegadaExpdt, EXP.HoraPrevistaSalidaExpdt) AS FechaExpedicion,
        CASE
            WHEN E.PutWallExtraccion = 1 THEN 'PutWall'
            WHEN E.MultiOrderExtraccion = 1 THEN 'Multiorder'
            WHEN E.PickingUnitarioExtraccion = 1 THEN 'Unitarios'
            WHEN E.ClaseExtraccion = 'G' THEN 'Consol'
            WHEN E.ClaseExtraccion = 'A' THEN 'Single'
            ELSE E.TipoExtraccion
        END AS TipoExtraccion,
        MAX(EP.PrioridadExtraccion) AS Prioridad,
        E.ID_UsuarioAsignaMuelle AS ID_UsuarioMuelle,
        E.RTTiempoMaxExtr AS TiempoMaximo,
        CASE
            WHEN E.FechaUbicacionMuelle IS NULL THEN 0
            ELSE DATEDIFF(MINUTE, E.FechaUbicacionMuelle, GETDATE())
        END AS TiempoTranscurrido,
        E.FechaProcesoExtraccion AS FechaProcesoExtraccion,
        RTRIM(AD.CodigoAlmacen) + ' ' +
        CASE
            WHEN E.ClaseExtraccion = 'A' THEN RTRIM(MAX(DIR2.NombreDireccion))
            ELSE RTRIM(AD.NombreAlmacen)
        END AS Destino,
        ISNULL(CAST(HR.NumeroHoja AS varchar(50)), '') AS NumeroHoja,
        HR.ID_HojaRuta AS ID_HojaRuta,
        ISNULL(MAX(EXD.OrdenDeCarga), 0) AS OrdenDeCarga,
        TC.CodigoCircuito AS CodigoCircuito,
        CASE
            WHEN SUM(CASE WHEN EP.EsPicking = 0 AND UBI.ID_TipoUbicacion IN (7,8) THEN 1 ELSE 0 END) > 0 THEN 1
            ELSE 0
        END AS CompletosEnPicking
    FROM ExtraccionesPlanning EP WITH (NOLOCK)
    INNER JOIN DOCS_BASE DB
        ON EP.ID_Cliente = DB.ID_Cliente
       AND EP.ID_Doc = DB.ID_Doc
    INNER JOIN Extracciones E WITH (NOLOCK)
        ON E.ID_Extraccion = EP.ID_Extraccion
    INNER JOIN Depositos DEP WITH (NOLOCK)
        ON EP.ID_Deposito = DEP.ID_Deposito
    INNER JOIN
    (
        SELECT
            ID_Cliente,
            ID_ProdClte,
            (
                CASE WHEN ID_UndAlmacenaje <= 1 THEN UndEstucheProdClte ELSE 1 END *
                CASE WHEN ID_UndAlmacenaje <= 2 THEN EstCajaProdClte ELSE 1 END *
                CASE WHEN ID_UndAlmacenaje <= 3 THEN CajasPaletProdClte ELSE 1 END
            ) AS FactorPalets,
            (
                CASE WHEN ID_UndAlmacenaje <= 1 THEN UndEstucheProdClte ELSE 1 END *
                CASE WHEN ID_UndAlmacenaje <= 2 THEN EstCajaProdClte ELSE 1 END
            ) AS FactorCajas,
            (
                CASE WHEN ID_UndAlmacenaje <= 1 THEN UndEstucheProdClte ELSE 1 END
            ) AS FactorEstuches,
            PaletsPorBase
        FROM ProductosClientes WITH (NOLOCK)
        WHERE ID_TipoProducto = 1
    ) PROD
        ON PROD.ID_Cliente = EP.ID_Cliente
       AND PROD.ID_ProdClte = EP.ID_ProdClte
    LEFT JOIN Ubicaciones UBI WITH (NOLOCK)
        ON EP.ID_Ubicacion = UBI.ID_Ubicacion
    LEFT JOIN ExpedienteDetalle EXD WITH (NOLOCK)
        ON E.ID_Extraccion = EXD.ID_Extraccion
       AND E.ID_Expediente = EXD.ID_Expediente
    LEFT JOIN Expedientes EXP WITH (NOLOCK)
        ON E.ID_Expediente = EXP.ID_Expediente
    LEFT JOIN HojasRuta HR WITH (NOLOCK)
        ON EXP.ID_HojaRuta = HR.ID_HojaRuta
    LEFT JOIN TiposCircuitos TC WITH (NOLOCK)
        ON E.ID_Circuito = TC.ID_Circuito
    LEFT JOIN Direcciones DIR2 WITH (NOLOCK)
        ON DB.ID_Cliente = DIR2.ID_Cliente
       AND DB.ID_Doc = DIR2.ID_Doc
       AND DIR2.ID_TipoDireccion = 1
    LEFT JOIN DivisionCliente DC WITH (NOLOCK)
        ON DB.ID_DivisionCliente = DC.ID_DivisionCliente
    INNER JOIN Almacenes AD WITH (NOLOCK)
        ON E.ID_AlmacenDestino = AD.ID_Almacen
    LEFT JOIN PaletPicking PP WITH (NOLOCK)
        ON PP.ID_PaletPicking = EP.ID_PaletPicking
    LEFT JOIN PaletPickingUbicacion PPU WITH (NOLOCK)
        ON PP.ID_PaletPicking = PPU.ID_PaletPicking
    LEFT JOIN Ubicaciones UPP WITH (NOLOCK)
        ON PPU.ID_Ubicacion = UPP.ID_Ubicacion
    WHERE EP.ID_TipoMovimiento = 'S'
      AND E.TipoExtraccion = 'S'
    GROUP BY
        EP.ID_Cliente,
        EP.ID_Doc,
        E.ID_Extraccion,
        E.ID_Expediente,
        E.ID_UbicacionMuelle,
        EP.ID_Deposito,
        E.FechaUbicacionMuelle,
        EXP.HoraPrevistaLlegadaExpdt,
        EXP.HoraPrevistaSalidaExpdt,
        E.PutWallExtraccion,
        E.MultiOrderExtraccion,
        E.PickingUnitarioExtraccion,
        E.ClaseExtraccion,
        E.TipoExtraccion,
        E.ID_UsuarioAsignaMuelle,
        E.RTTiempoMaxExtr,
        E.FechaProcesoExtraccion,
        AD.CodigoAlmacen,
        AD.NombreAlmacen,
        HR.NumeroHoja,
        HR.ID_HojaRuta,
        TC.CodigoCircuito
),
TEO AS
(
    SELECT
        LD.ID_Cliente,
        LD.ID_Doc,
        SUM(CAST(LD.PaletsCompletosLineaDoc AS float)) AS PaletsTeo,
        SUM(CAST(LD.CajasCompletasLineaDoc  AS float)) AS CajasTeo
    FROM XGA.dbo.LineasDocumentos LD WITH (NOLOCK)
    INNER JOIN DOCS_BASE DB
        ON LD.ID_Cliente = DB.ID_Cliente
       AND LD.ID_Doc     = DB.ID_Doc
    WHERE LD.TipoMovimientoLineaDoc = 'S'
    GROUP BY LD.ID_Cliente, LD.ID_Doc
),
PEND_BASE AS
(
    SELECT
        Documentos.ID_Cliente AS ID_Cliente,
        Ubicaciones.ZonaUbicacion + '-' + Ubicaciones.PasilloUbicacion + '-' + Ubicaciones.HuecoUbicacion + '-' + Ubicaciones.NivelUbicacion AS Ubicacion,
        Expedientes.ID_Expediente AS ID_Expediente,
        EstadosDocumentos.ID_Extraccion AS ID_Extraccion,
        Documentos.AlbaranDoc AS Documento,
        COUNT(DISTINCT MP.ID_PaletPicking) AS SSCCTotales,
        COUNT(DISTINCT PaletPickingExpediente.ID_PaletPicking) AS SSCCCargados,
        Expedientes.HoraPrevistaLlegadaExpdt AS HoraPrevistaLlegadaExpdt
    FROM DOCS_BASE Documentos
    INNER JOIN XGA.dbo.ExpedienteDetalle ExpedienteDetalle WITH (NOLOCK)
        ON Documentos.ID_ExpedienteDetalle = ExpedienteDetalle.ID_ExpedienteDetalle
    INNER JOIN XGA.dbo.Ubicaciones Ubicaciones WITH (NOLOCK)
        ON Ubicaciones.ID_Ubicacion = ExpedienteDetalle.ID_UbicacionPlayaExpteDetalle
    INNER JOIN XGA.dbo.Expedientes Expedientes WITH (NOLOCK)
        ON Expedientes.ID_Expediente = ExpedienteDetalle.ID_Expediente
    INNER JOIN XGA.dbo.EstadosDocumentos EstadosDocumentos WITH (NOLOCK)
        ON Documentos.ID_Cliente = EstadosDocumentos.ID_Cliente
       AND Documentos.ID_Doc = EstadosDocumentos.ID_Doc
       AND EstadosDocumentos.ID_TipoEstado = 2
    INNER JOIN XGA.dbo.PlayasAsignadas PlayasAsignadas WITH (NOLOCK)
        ON PlayasAsignadas.ID_UbicacionPlaya = ExpedienteDetalle.ID_UbicacionPlayaExpteDetalle
       AND PlayasAsignadas.ID_Cliente = Documentos.ID_Cliente
       AND PlayasAsignadas.ID_Doc = Documentos.ID_Doc
    INNER JOIN XGA.dbo.Direcciones Direcciones WITH (NOLOCK)
        ON Documentos.ID_Cliente = Direcciones.ID_Cliente
       AND Documentos.ID_Doc = Direcciones.ID_Doc
       AND Direcciones.ID_TipoDireccion = 1
    LEFT JOIN XGA.dbo.HojasRuta HojasRuta WITH (NOLOCK)
        ON HojasRuta.ID_HojaRuta = Expedientes.ID_HojaRuta
    LEFT JOIN MP_S MP
        ON Documentos.ID_Cliente = MP.ID_Cliente
       AND Documentos.ID_Doc = MP.ID_Doc
    LEFT JOIN XGA.dbo.PaletPickingExpediente PaletPickingExpediente WITH (NOLOCK)
        ON MP.ID_PaletPicking = PaletPickingExpediente.ID_PaletPicking
    WHERE Ubicaciones.ID_Almacen = 221
      AND Ubicaciones.ID_TipoUbicacion = 6
      AND Documentos.ID_UltimoTipoEstado IN (1, 2, 3)
    GROUP BY
        Documentos.ID_Cliente,
        Ubicaciones.ZonaUbicacion,
        Ubicaciones.PasilloUbicacion,
        Ubicaciones.HuecoUbicacion,
        Ubicaciones.NivelUbicacion,
        Expedientes.ID_Expediente,
        EstadosDocumentos.ID_Extraccion,
        Documentos.AlbaranDoc,
        Expedientes.HoraPrevistaLlegadaExpdt
),
PEND AS
(
    SELECT
        ID_Cliente,
        ID_Expediente,
        ID_Extraccion,
        Documento,
        STRING_AGG(Ubicacion, ' | ') AS UbicacionesPendientesCarga,
        SUM(SSCCTotales) AS SSCCTotales,
        SUM(SSCCCargados) AS SSCCCargados,
        SUM(SSCCTotales) - SUM(SSCCCargados) AS SSCCPendientesCarga,
        MAX(HoraPrevistaLlegadaExpdt) AS HoraPrevistaLlegadaExpdt
    FROM PEND_BASE
    GROUP BY
        ID_Cliente,
        ID_Expediente,
        ID_Extraccion,
        Documento
),
ESTADOS_DOC AS
(
    SELECT
        ED.ID_Cliente,
        ED.ID_Doc,
        MAX(CASE WHEN ED.ID_TipoEstado = 1 THEN ED.FechaProcesoEstado END) AS FechaHoraEstado10,
        MAX(CASE WHEN ED.ID_TipoEstado = 2 THEN ED.FechaProcesoEstado END) AS FechaHoraEstado20,
        MAX(CASE WHEN ED.ID_TipoEstado = 3 THEN ED.FechaProcesoEstado END) AS FechaHoraEstado30,
        MAX(CASE WHEN ED.ID_TipoEstado = 4 THEN ED.FechaProcesoEstado END) AS FechaHoraEstado40
    FROM XGA.dbo.EstadosDocumentos ED WITH (NOLOCK)
    INNER JOIN DOCS_BASE DB
        ON ED.ID_Cliente = DB.ID_Cliente
       AND ED.ID_Doc = DB.ID_Doc
    WHERE ED.ID_TipoEstado IN (1, 2, 3, 4)
    GROUP BY
        ED.ID_Cliente,
        ED.ID_Doc
),
SHIP_CHECK AS
(
    SELECT
        D.ShipmentNumberDoc,
        COUNT(DISTINCT TAB.ID_Expediente) AS NumExpedientes
    FROM DOCS_BASE D
    LEFT JOIN TAB
        ON D.ID_Cliente = TAB.ID_Cliente
       AND D.ID_Doc = TAB.ID_Doc
    WHERE D.ShipmentNumberDoc IS NOT NULL
      AND LTRIM(RTRIM(CAST(D.ShipmentNumberDoc AS varchar(50)))) <> ''
      AND TAB.ID_Expediente IS NOT NULL
      AND TAB.ID_Expediente <> -1
    GROUP BY D.ShipmentNumberDoc
)
SELECT
    CASE
        WHEN D.FechaTeoricaCargaDoc IS NULL THEN ''
        WHEN CAST(D.FechaTeoricaCargaDoc AS date) = DATEADD(day, -1, CAST(GETDATE() AS date)) THEN 'Ayer'
        WHEN CAST(D.FechaTeoricaCargaDoc AS date) <  CAST(GETDATE() AS date) THEN 'Backlog'
        WHEN CAST(D.FechaTeoricaCargaDoc AS date) =  CAST(GETDATE() AS date) THEN 'Hoy'
        WHEN CAST(D.FechaTeoricaCargaDoc AS date) = DATEADD(day, 1, CAST(GETDATE() AS date)) THEN 'Mañana'
        WHEN CAST(D.FechaTeoricaCargaDoc AS date) = DATEADD(day, 2, CAST(GETDATE() AS date)) THEN 'Pasado mañana'
        ELSE 'Futuro'
    END AS [1_EstadoFechaTeoricaCarga],
    D.AlbaranDoc AS [2_Albaran],
    TAB.ID_Extraccion AS [3_ID_Extraccion],
    CASE
        WHEN TAB.ID_Expediente = -1 THEN ''
        ELSE CAST(TAB.ID_Expediente AS varchar(50))
    END AS [4_ID_Expediente],
    D.FechaTeoricaCargaDoc AS [5_FechaTeoricaCargaDoc],
    CASE
        WHEN D.ID_UltimoTipoEstado IN (1,2,3) THEN 'Abierto'
        WHEN D.ID_UltimoTipoEstado = 4 THEN 'Cerrado'
        ELSE NULL
    END AS [6_EstadoAbiertoCerrado],
    CASE
        WHEN D.ID_UltimoTipoEstado = 2
             AND ISNULL(TAB.TotalPalets, 0) > 0
             AND (ISNULL(TAB.TotalPaletsLeidos, 0) * 100.0) / TAB.TotalPalets >= 100
             AND (
                    ISNULL(TAB.PickingCajas, 0) = 0
                 OR (ISNULL(TAB.PickingCajasLeidas, 0) * 100.0) / NULLIF(TAB.PickingCajas, 0) >= 100
                 )
             AND ISNULL(PEND.SSCCPendientesCarga, 0) = 0
             AND ISNULL(TAB.TiempoTranscurrido, 0) > 60
        THEN '20-INC'
        ELSE
            CASE D.ID_UltimoTipoEstado
                WHEN 1 THEN '10'
                WHEN 2 THEN '20'
                WHEN 3 THEN '30'
                WHEN 4 THEN '40'
                ELSE NULL
            END
    END AS [7_TipoEstadoConvertido],
    ESTADOS_DOC.FechaHoraEstado10 AS [8_FechaHoraEstado10],
    ESTADOS_DOC.FechaHoraEstado20 AS [9_FechaHoraEstado20],
    ESTADOS_DOC.FechaHoraEstado30 AS [10_FechaHoraEstado30],
    ESTADOS_DOC.FechaHoraEstado40 AS [11_FechaHoraEstado40],
    ISNULL(EDO.FechaPactadaEstado, ISNULL(D.FechaProgramadaDoc, D.FechaTeoricaServicioDoc)) AS [12_FechaMinima],
    ISNULL(DIR.NombreDireccion, 'crossdocking') AS [13_NombreDireccion],
    DOL.ObservacionesLogisticas AS [14_Comentario],
    ISNULL(RTRIM(RR.RutaReparto), '')
        + CASE
            WHEN D.ShipmentNumberDoc IS NOT NULL
             AND LTRIM(RTRIM(CAST(D.ShipmentNumberDoc AS varchar(50)))) <> ''
            THEN '_' + LTRIM(RTRIM(CAST(D.ShipmentNumberDoc AS varchar(50))))
                 + CASE
                     WHEN SC.NumExpedientes IS NULL OR SC.NumExpedientes <= 1 THEN '_OK'
                     ELSE '_ERROR(' + CAST(SC.NumExpedientes AS varchar(10)) + 'exp)'
                   END
            ELSE ''
          END AS [15_RutaReparto],
    CAST(COALESCE(NULLIF(TAB.PaletsCompletos, 0), TEO.PaletsTeo, 0) AS float) AS [16_PaletsCompletos],
    CAST(COALESCE(NULLIF(ISNULL(TAB.PaletsBases,0) + ISNULL(TAB.PaletsPickingBase,0), 0),
                  TEO.PaletsTeo, 0) AS int) AS [17_PaletsBases],
    CAST(
        CASE
            WHEN ISNULL(TAB.PaletsCompletos, 0) = 0 THEN 0
            ELSE (ISNULL(TAB.PaletsCompletosLeidos, 0) * 100.0) / TAB.PaletsCompletos
        END AS float
    ) AS [18_PorcPaletsCompletos],
    CAST(COALESCE(NULLIF(TAB.TotalPalets, 0), TEO.PaletsTeo, 0) AS float) AS [19_TotalPalets],
    CAST(
        CASE
            WHEN D.ID_UltimoTipoEstado IN (3, 4) THEN 0
            WHEN TAB.ID_Cliente IS NULL THEN ISNULL(TEO.PaletsTeo, 0)
            WHEN ISNULL(TAB.TotalPalets, 0) = 0 THEN 0
            ELSE ROUND(
                ISNULL(TAB.TotalPalets, 0) *
                (
                    1 -
                    (
                        CASE
                            WHEN ISNULL(TAB.PaletsCompletos, 0) = 0 THEN 0
                            ELSE (ISNULL(TAB.PaletsCompletosLeidos, 0) * 100.0) / TAB.PaletsCompletos
                        END
                    ) / 100.0
                ),
                0
            )
        END AS int
    ) AS [20_PendientePalets],
    LTRIM(STR(
        CASE
            WHEN ISNULL(TAB.TotalPalets, 0) = 0 THEN 0
            ELSE (ISNULL(TAB.TotalPaletsLeidos, 0) * 100.0) / TAB.TotalPalets
        END, 10, 1
    )) AS [21_PorcTotalPalets],
    COALESCE(NULLIF(TAB.PickingCajas, 0), TEO.CajasTeo, 0) AS [22_PickingCajas],
    CASE
        WHEN ISNULL(TAB.PickingCajas, 0) = 0 THEN 0
        ELSE (ISNULL(TAB.PickingCajasLeidas, 0) * 100.0) / TAB.PickingCajas
    END AS [23_PorcPickingCajas],
    CAST(
        CASE
            WHEN D.ID_UltimoTipoEstado IN (3, 4) THEN 0
            WHEN TAB.ID_Cliente IS NULL THEN ISNULL(TEO.CajasTeo, 0)
            WHEN ISNULL(TAB.PickingCajas, 0) = 0 THEN 0
            ELSE ROUND(
                ISNULL(TAB.PickingCajas, 0) *
                (
                    1 -
                    (
                        CASE
                            WHEN ISNULL(TAB.PickingCajas, 0) = 0 THEN 0
                            ELSE (ISNULL(TAB.PickingCajasLeidas, 0) * 100.0) / TAB.PickingCajas
                        END
                    ) / 100.0
                ),
                0
            )
        END AS int
    ) AS [24_PickPend],
    TAB.PickingUnidades AS [25_PickingUnidades],
    CASE
        WHEN ISNULL(TAB.PickingUnidades, 0) = 0 THEN 0
        ELSE (ISNULL(TAB.PickingUnidadesLeidas, 0) * 100.0) / TAB.PickingUnidades
    END AS [26_PorcPickingUnidades],
    TAB.Picks AS [27_Picks],
    CASE
        WHEN ISNULL(TAB.Picks, 0) = 0 THEN 0
        ELSE (ISNULL(TAB.PicksLeidos, 0) * 100.0) / TAB.Picks
    END AS [28_PorcPicks],
    TAB.TiempoTranscurrido AS [29_TiempoTranscurrido],
    TAB.Destino AS [30_Destino],
    PEND.UbicacionesPendientesCarga AS [31_UbicacionesPendientesCarga],
    ISNULL(PEND.SSCCTotales, 0) AS [32_SSCCTotales],
    ISNULL(PEND.SSCCCargados, 0) AS [33_SSCCCargados],
    ISNULL(PEND.SSCCPendientesCarga, 0) AS [34_SSCCPendientesCarga],
    PEND.HoraPrevistaLlegadaExpdt AS [35_HoraPrevistaLlegadaExpdt]
FROM DOCS_BASE D
LEFT JOIN Direcciones DIR WITH (NOLOCK)
    ON D.ID_Cliente = DIR.ID_Cliente
   AND D.ID_Doc = DIR.ID_Doc
   AND DIR.ID_TipoDireccion = 1
LEFT JOIN EstadosDocumentos EDO WITH (NOLOCK)
    ON D.ID_UltimoEstado = EDO.ID_Estado
LEFT JOIN DocumentosObservacionesLogisticas DOL WITH (NOLOCK)
    ON DOL.ID_Cliente = DIR.ID_Cliente
   AND DOL.CodigoDireccion = DIR.CodigoDireccion
LEFT JOIN RutasReparto RR WITH (NOLOCK)
    ON D.ID_RutaReparto = RR.ID_RutaReparto
LEFT JOIN TAB
    ON D.ID_Cliente = TAB.ID_Cliente
   AND D.ID_Doc = TAB.ID_Doc
LEFT JOIN TEO
    ON D.ID_Cliente = TEO.ID_Cliente
   AND D.ID_Doc = TEO.ID_Doc
LEFT JOIN PEND
    ON D.ID_Cliente = PEND.ID_Cliente
   AND TAB.ID_Extraccion = PEND.ID_Extraccion
   AND TAB.ID_Expediente = PEND.ID_Expediente
   AND D.AlbaranDoc = PEND.Documento
LEFT JOIN ESTADOS_DOC
    ON D.ID_Cliente = ESTADOS_DOC.ID_Cliente
   AND D.ID_Doc = ESTADOS_DOC.ID_Doc
LEFT JOIN SHIP_CHECK SC
    ON D.ShipmentNumberDoc = SC.ShipmentNumberDoc
ORDER BY D.FechaTeoricaCargaDoc ASC