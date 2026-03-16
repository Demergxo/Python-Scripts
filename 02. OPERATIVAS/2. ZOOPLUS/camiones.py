import pandas as pd
import openpyxl
from datetime import datetime
import sys
import os
usuario = os.environ['USERNAME']

def procesar_archivos(archivo1, archivo2):
    # Leer datos del primer archivo (Pallets Mover RACK)
    df_pallets = pd.read_excel(archivo1, sheet_name="Pallets Mover RACK", skiprows=5, usecols=["Location", "LA", "Descripción Larga", "NÂ° Support"], dtype={"NÂ° Support": str})
    df_pallets.rename(columns={"Location": "Ubicación", "NÂ° Support": "Soporte", "Descripción Larga": "Descripción"}, inplace=True)

    # Leer datos del segundo archivo (Resumen y Stock by Location)
    df_resumen = pd.read_excel(archivo2, sheet_name="Resumen", usecols=["LA", "Ubicación", "Soporte", "Condición01"], dtype={"Soporte": str})
    df_stock = pd.read_excel(archivo2, sheet_name="Stock by Location", usecols=["ArtÃ­culo", "DesignaciÃ³n"])

    # Filtrar solo donde "Condición01" sea "Si"
    df_resumen = df_resumen[df_resumen["Condición01"] == "Si"]

    # Unir "Resumen" con "Stock by Location" para obtener la descripción
    df_resumen = df_resumen.merge(df_stock, left_on="LA", right_on="ArtÃ­culo", how="left").drop(columns=["ArtÃ­culo", "Condición01"])
    df_resumen.rename(columns={"DesignaciÃ³n": "Descripción"}, inplace=True)

    df_resumen = df_resumen.drop_duplicates(subset=["Ubicación", "LA", "Soporte"])
    df_pallets = df_pallets.drop_duplicates(subset=["Ubicación", "LA", "Soporte"])

    # Unir "Pallets Mover RACK" con "Resumen" para cruzar la información
    df_final = pd.concat([df_pallets, df_resumen], ignore_index=True).drop_duplicates()

    # Ordenar por "Ubicación"
    df_final.sort_values(by="Ubicación", inplace=True)

    # Dividir en bloques de 33 filas y asignar a 40 pestañas
    num_camiones = 40
    filas_por_camion = 33
    escritor = pd.ExcelWriter(f"C:\\Users\\{usuario}\\OneDrive - GXO\\Escritorio\\camiones_{datetime.today().strftime('%Y-%m-%d')}.xlsx", engine='xlsxwriter')

    for i in range(num_camiones):
        inicio = i * filas_por_camion
        fin = inicio + filas_por_camion
        df_camion = df_final.iloc[inicio:fin]

        # Escribir en la hoja "Camión xx" con formato de tabla
        if not df_camion.empty:
            df_camion.to_excel(escritor, sheet_name=f"Camión {i+1:02}", index=False, startrow=0)

            workbook = escritor.book
            worksheet = escritor.sheets[f"Camión {i+1:02}"]

            # Crear tabla en Excel
            num_filas, num_columnas = df_camion.shape
            worksheet.add_table(0, 0, num_filas, num_columnas - 1, {
                'columns': [{'header': col} for col in df_camion.columns]
            })

    # Guardar archivo final
    escritor.close()
    print(f"Archivo generado: camiones_{datetime.today().strftime('%Y-%m-%d')}.xlsx")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Uso: python camiones.py <archivo1.xlsx> <archivo2.xlsx>")
    else:
        procesar_archivos(sys.argv[1], sys.argv[2])
