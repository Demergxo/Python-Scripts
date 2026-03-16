import os
import sys
import pandas as pd


def buscar_en_archivo(ruta_archivo, texto_buscar):
    try:
        # Cargar todas las hojas
        hojas = pd.read_excel(ruta_archivo, sheet_name=None, dtype=str)

        resultados = []

        for nombre_hoja, df in hojas.items():
            # Convertir todo a string para evitar problemas
            df = df.astype(str)

            for fila_idx, fila in df.iterrows():
                for col_idx, valor in enumerate(fila):
                    if texto_buscar.lower() in str(valor).lower():
                        resultados.append({
                            "archivo": os.path.basename(ruta_archivo),
                            "hoja": nombre_hoja,
                            "fila": fila_idx + 2,  # type:ignore +2 por índice y cabecera
                            "columna": df.columns[col_idx],
                            "valor": valor
                        })

        return resultados

    except Exception as e:
        print(f"Error leyendo {ruta_archivo}: {e}")
        return []


def buscar_en_carpeta(ruta_carpeta, texto_buscar):
    resultados_totales = []

    for archivo in os.listdir(ruta_carpeta):
        if archivo.endswith(".xlsx"):
            ruta_completa = os.path.join(ruta_carpeta, archivo)
            resultados = buscar_en_archivo(ruta_completa, texto_buscar)
            resultados_totales.extend(resultados)

    return resultados_totales


if __name__ == "__main__":

    if len(sys.argv) != 3:
        print("Uso: python busqueda.py <carpeta> <palabra>")
        sys.exit(1)

    carpeta = sys.argv[1]
    palabra = sys.argv[2]

    resultados = buscar_en_carpeta(carpeta, palabra)

    if resultados:
        print("\n🔎 Resultados encontrados:\n")
        for r in resultados:
            print(
                f"Archivo: {r['archivo']} | "
                f"Hoja: {r['hoja']} | "
                f"Fila: {r['fila']} | "
                f"Columna: {r['columna']} | "
                f"Valor: {r['valor']}"
            )
    else:
        print("\nNo se encontraron coincidencias.")