    SELECT 
        RTRIM(AlbaranDoc) AS AlbaranDoc,
        '672487-GXO LOGISTICS SPAIN SLU' AS 'Sub-Account', 'SAN FERNANDO' AS 'Depot Information', RTRIM(AlbaranDoc) AS 'Customer Reference',
        'Taisa Logistics' AS 'Origin Address Reference', 'Taisa Logistics' AS 'Origin Address – Name', 'Av. la Veguilla, 20, Nave A' AS 'Origin Address Line 1',
        '' AS 'Origin Address Line 2', 'Cabanillas del Campo' AS 'Origin City', 'ES' as 'Origin – Country', 
        '19171' AS 'Origin – Zipcode', '' AS 'Pick up instructions', FechaDoc AS 'Pickup Date DD/MM/YYYY',
        'Before' AS 'Date Flexibility', '13:00' AS 'Pickup Time (HH:MM 24hr format)', 'Before' AS 'Time Flexibility',
        '' AS 'Destination Address Reference', RTRIM(NombreDireccion) AS 'Destination Address – Name', RTRIM(Direccion1Direccion) AS 'Destination Address Line 1',
        '' AS 'Destination - Address Line 2', PoblacionDireccion AS 'Destination City', 'ES' as 'Destination – Country',
        CodigoPostal AS 'Destination – Zipcode', ObsDocumento1 AS 'Delivery instructions', '' AS 'Delivery Date DD/MM/YYYY',
        'Before' AS 'Delivery Date Flexibility', '22:00' AS 'Delivery Time (HH:MM 24hr format)', 'Before' AS 'Delivery Time Flexibility', RTRIM(AlbaranDoc) + '/' + PedidoDestinatarioDoc AS 'Special Instructions',
        'EUR' AS 'Commodity1', '1' AS 'Quantity1', ROUND(PesoFiege, 0) AS 'Weight1', ROUND(volumenFiege, 0) AS 'Volume1','' AS 'LinearMeter1',
        '' AS 'Commodity2', '' AS 'Quantity2', '' AS 'Weight2', '' AS 'Volume2','' AS 'LinearMeter2',
        '' AS 'Commodity3', '' AS 'Quantity3', '' AS 'Weight3', '' AS 'Volume3','' AS 'LinearMeter3',
        '' AS 'Commodity4', '' AS 'Quantity4', '' AS 'Weight4', '' AS 'Volume4','' AS 'LinearMeter4',
        '' AS 'Commodity5', '' AS 'Quantity5', '' AS 'Weight5', '' AS 'Volume5',
        '' AS 'Hazmat (Y/N)',
        '' AS 'UN #1', '' AS 'Label 1', '' AS 'Limited Quantity 1 (Y/N)', '' AS 'Packing Group 1','' AS 'Packages 1', '' AS 'Quantity 1', '' AS 'Size/Weight 1', '' AS 'UOM 1',
        '' AS 'UN #2', '' AS 'Label 2', '' AS 'Limited Quantity 2 (Y/N)', '' AS 'Packing Group 2','' AS 'Packages 2', '' AS 'Quantity 2', '' AS 'Size/Weight 2', '' AS 'UOM 2',
        '' AS 'UN #3', '' AS 'Label 3', '' AS 'Limited Quantity 3 (Y/N)', '' AS 'Packing Group 3','' AS 'Packages 3', '' AS 'Quantity 3', '' AS 'Size/Weight 3', '' AS 'UOM 3',
        '' AS 'UN #4', '' AS 'Label 4', '' AS 'Limited Quantity 4 (Y/N)', '' AS 'Packing Group 4','' AS 'Packages 4', '' AS 'Quantity 4', '' AS 'Size/Weight 4', '' AS 'UOM 4',
        '' AS 'UN #5', '' AS 'Label 5', '' AS 'Limited Quantity 5 (Y/N)', '' AS 'Packing Group 5','' AS 'Packages 5', '' AS 'Quantity 5', '' AS 'Size/Weight 5', '' AS 'UOM 5', 
        '' AS 'LinearMeter5',
        '' AS 'Booking In(Y/N)', '' AS 'Contact Name', '' AS 'Telephone Number', '' AS 'Installation', '' AS 'Assembly', '' AS 'Return Rate','' AS 'Haulage',
        '' AS 'Origin Contact Name', '' AS 'Origin Contact Number', '' AS 'Origin Contact Email Address', '' AS 'Origin Send Tracking Link Email(Y/N)',
        '' AS 'Destination Contact Name', '' AS 'Destination Contact Number', '' AS 'Destination Contact Email Address', ''  AS 'Destination Send Tracking Link Email(Y/N)',
        '' AS 'Origin Contact Name(2)', '' AS 'Origin Contact Number(2)', '' AS 'Origin Contact Email Address(2)', '' AS 'Origin Send Tracking Link Email(2) (Y/N)',
        '' AS 'Destination Contact Name(2)', '' AS 'Destination Contact Number(2)', '' AS 'Destination Contact Email Address(2)', ''  AS 'Destination Send Tracking Link Email(2) (Y/N)',
        '' AS 'Origin Contact Name(3)', '' AS 'Origin Contact Number(3)', '' AS 'Origin Contact Email Address(3)', '' AS 'Origin Send Tracking Link Email(3) (Y/N)',
        '' AS 'Destination Contact Name(3)', '' AS 'Destination Contact Number(3)', '' AS 'Destination Contact Email Address(3)', ''  AS 'Destination Send Tracking Link Email(3) (Y/N)',
        '' AS 'Origin Contact Name(4)', '' AS 'Origin Contact Number(4)', '' AS 'Origin Contact Email Address(4)', '' AS 'Origin Send Tracking Link Email(4) (Y/N)',
        '' AS 'Destination Contact Name(4)', '' AS 'Destination Contact Number(4)', '' AS 'Destination Contact Email Address(4)', ''  AS 'Destination Send Tracking Link Email(4) (Y/N)',
        '' AS 'Origin Contact Name(5)', '' AS 'Origin Contact Number(5)', '' AS 'Origin Contact Email Address(5)', '' AS 'Origin Send Tracking Link Email(5) (Y/N)',
        '' AS 'Destination Contact Name(5)', '' AS 'Destination Contact Number(5)', '' AS 'Destination Contact Email Address(5)', ''  AS 'Destination Send Tracking Link Email(5) (Y/N)'


    FROM
        vDocumentos
    WHERE 
        ID_Cliente = 944
        AND NombreTipoDocumento = 'Albaran'
        AND RutaReparto = 'MSMALOXPO'
        AND CONVERT(date, FechaDoc) BETWEEN CONVERT(date, :inicio) AND CONVERT(date, :fin) 


SELECT
    RTRIM(AlbaranDoc), FechaTeoricaCargaDoc
FROM
    Documentos
WHERE
    ID_Cliente= 944
    AND CONVERT(date, FechaDoc) BETWEEN CONVERT(date, :inicio) AND CONVERT(date, :fin) 