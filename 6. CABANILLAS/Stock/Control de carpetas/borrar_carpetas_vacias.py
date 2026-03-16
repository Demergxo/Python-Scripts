import os

def eliminar_carpetas_vacias(ruta):
    # Recorre todas las carpetas en la ruta dada
    for root, dirs, files in os.walk(ruta, topdown=False):
        for dir_name in dirs:
            carpeta = os.path.join(root, dir_name)
            # Verifica si la carpeta está vacía
            if len(os.listdir(carpeta)) == 0:
                try:
                    # Elimina la carpeta vacía
                    os.rmdir(carpeta)
                    print(f'[+] Carpeta vacía eliminada: {carpeta}')
                except OSError as e:
                    print(f'[!] Error al eliminar la carpeta {carpeta}: {e}')

def main():
    # Solicitar la ruta donde se eliminarán las carpetas vacías
    ruta = input("[?] Ingrese la ruta donde desea eliminar las carpetas vacías: ")
    
    # Llamar a la función para eliminar las carpetas vacías
    eliminar_carpetas_vacias(ruta)

if __name__ == "__main__":
    main()
