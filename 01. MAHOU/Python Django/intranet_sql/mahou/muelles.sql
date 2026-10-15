SELECT
    CONCAT(U.ZonaUbicacion, '-', U.PasilloUbicacion, '-', U.HuecoUbicacion, '-', U.NivelUbicacion) AS UbicacionCompleta,
    U.ID_Ubicacion,
    
    COUNT(P.SSCCPalet) AS NumPalets,

    MIN(CONVERT(date, P.EntradaPalet)) AS FechaEntradaMin

FROM XGA.dbo.Ubicaciones U
LEFT JOIN XGA.dbo.Palets P
       ON P.ID_Ubicacion = U.ID_Ubicacion
      AND P.ID_Almacen   = U.ID_Almacen
      AND P.CantidadActualPalet > 0

WHERE U.ID_Almacen = 221
  AND U.ZonaUbicacion IN ('DE', '88')

GROUP BY
    U.ID_Ubicacion,
    U.ZonaUbicacion,
    U.PasilloUbicacion,
    U.HuecoUbicacion,
    U.NivelUbicacion

ORDER BY 
    U.PasilloUbicacion, 
    U.HuecoUbicacion, 
    U.NivelUbicacion;