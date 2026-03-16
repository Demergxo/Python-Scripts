import os

# Ruta a la carpeta con los archivos .xlsx
CARPETA = r'C:\Users\jgmeras\OneDrive - GXO\Escritorio\Ajustes Altura\SbL'

# Prefijo estándar
PREFIJO = "ES_ZOOPLUS_STOCK_POR_UBICACION_"

def renombrar_archivos(carpeta):
    archivos = [f for f in os.listdir(carpeta) if f.lower().endswith(".xlsx")]
    total = len(archivos)
    renombrados = []

    for idx, nombre in enumerate(archivos, start=1):
        print(f"🧪 Procesando {idx}/{total}: {nombre}")

        ultimos_20 = nombre[-20:]
        nuevo_nombre = PREFIJO + ultimos_20

        ruta_origen = os.path.join(carpeta, nombre)
        ruta_destino = os.path.join(carpeta, nuevo_nombre)

        try:
            os.rename(ruta_origen, ruta_destino)
            renombrados.append((nombre, nuevo_nombre))
        except Exception as e:
            print(f"❌ Error al renombrar '{nombre}': {e}")

    print("\n📋 Resumen:")
    if renombrados:
        print("Archivos renombrados:")
        for original, nuevo in renombrados:
            print(f" - {original} ➜ {nuevo}")
    else:
        print("No se renombró ningún archivo.")

if __name__ == "__main__":
    renombrar_archivos(CARPETA)
