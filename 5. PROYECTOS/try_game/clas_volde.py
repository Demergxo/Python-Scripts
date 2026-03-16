import shutil
import re
import os

def seleccionar_archivo_xlsx(nombre_archivo):
    if nombre_archivo.endswith('.xlsx'):
        return "xlsx"
    else:
        return None
    
def clasificar_archivo(nombre_archivo, directorios, ruta_origen):
    res = seleccionar_archivo_xlsx(nombre_archivo)
    if res == "xlsx":
        regex_file = r"-(\d{2})-"
        match = re.search(regex_file, nombre_archivo)
        if match:
            for primeros_dos_caracteres, ruta_completa in directorios:
                if primeros_dos_caracteres == match.group(1):
                    shutil.copyfile(os.path.join(ruta_origen, nombre_archivo), os.path.join(ruta_completa, nombre_archivo))    

def leer_primeros_dos_caracteres_directorios(ruta):
    # Verificar si la ruta existe y es un directorio
    if not os.path.isdir(ruta):
        print(f"La ruta {ruta} no es un directorio válido.")
        return
    
    resultados = []
    
    # Recorrer los directorios dentro de la ruta dada
    for nombre_directorio in os.listdir(ruta):
        ruta_completa = os.path.join(ruta, nombre_directorio)
        
        # Verificar si es un directorio
        if os.path.isdir(ruta_completa):
            # Leer los primeros 2 caracteres del nombre del directorio
            primeros_dos_caracteres = nombre_directorio[:2]
            resultados.append((primeros_dos_caracteres, ruta_completa))
    
    return resultados

def recorrer_archivos(directory):
    
    if not os.path.exists(directory):
        print(f"La ruta {directory} no existe.")
        return []
    
    nombres_archivos = []
    
    # Recorrer los directorios y archivos dentro de la ruta dada
    for directorio, subdirectorios, archivos in os.walk(directory):
        for archivo in archivos:
            nombres_archivos.append(archivo)
    
    return nombres_archivos

def main():
    ruta_origen = input("Ingrese la ruta del directorio origen: ")
    ruta_destino = input("Ingrese la ruta del directorio destino: ")
    directorios = leer_primeros_dos_caracteres_directorios(ruta_destino)
    for nombre_archivo in recorrer_archivos(ruta_origen):
        clasificar_archivo(nombre_archivo, directorios, ruta_origen)
    print("Archivos clasificados correctamente.")   

if __name__ == "__main__":
    main()
