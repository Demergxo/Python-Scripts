import csv
import datetime
from alive_progress import alive_bar
from funciones import (
    leer_master_data,
    separar_por_delivery,
    catalogar_delivery_skus,
    procesar_datos,
    obtener_r_mayor,
    selector_muelle_pasillo
)

def main():
    # Inicializar el índice de familias
    indice = {
        "Dogs": [],
        "Cats": [],
        "Others": [],
        "Consumables": [],
        "Out of family": []
    }

    # Leer y procesar master data
    with alive_bar(1, title='Leyendo master data') as bar:
        indice = leer_master_data(indice)
        bar()

    # Separar por delivery
    with alive_bar(1, title='Separando por delivery') as bar:
        delivery_sku_dict = separar_por_delivery()
        bar()

    # Catalogar los SKU de cada delivery
    with alive_bar(1, title='Catalogando delivery SKUs') as bar:
        separator = catalogar_delivery_skus(delivery_sku_dict, indice)
        bar()

    # Procesar datos para obtener ubicaciones y volumetría
    with alive_bar(1, title='Procesando datos') as bar:
        result_dict = procesar_datos(delivery_sku_dict)
        bar()

    # Obtener la ubicación con mayor volumen para cada delivery
    with alive_bar(1, title='Obteniendo ubicación con mayor volumen') as bar:
        r_mayor_dict = obtener_r_mayor(result_dict)
        bar()

    # Preparar los datos finales para el CSV
    csv_data = []
    total_deliveries = len(r_mayor_dict)
    with alive_bar(total_deliveries, title='Preparando datos para CSV') as bar:
        for delivery, ubicacion in r_mayor_dict.items():
            muelle = selector_muelle_pasillo(ubicacion)
            csv_data.append({
                "delivery": delivery,
                "ubicacion": ubicacion,
                "muelle": muelle
            })
            bar()

    # Escribir los datos en un archivo CSV
    fecha = datetime.datetime.now().strftime("%Y%m%d")
    csv_filename = f"{fecha}resultado.csv"
    with alive_bar(1, title=f'Escribiendo archivo CSV ({csv_filename})') as bar:
        with open(csv_filename, mode='w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=["delivery", "ubicacion", "muelle"])
            writer.writeheader()
            for row in csv_data:
                writer.writerow(row)
        bar()

    print(f"Archivo CSV '{csv_filename}' creado con éxito.")

if __name__ == "__main__":
    main()

