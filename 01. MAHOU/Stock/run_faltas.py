import qry_pedidos_final_steel
import descarga_edi_steel
import qry_consulta_UBSPROD
import os
import pandas as pd

user = os.getenv("USERNAME")
path = os.getcwd()

def leer_csv(ruta_archivo):
    """
    Lee un archivo Excel y devuelve un DataFrame.
    """
    try:
        #leemos solo la columna A
        df = pd.read_csv(nombre_archivo, sep=";", encoding="utf-8-sig", dtype=str, usecols=["Albarán"])
        df["Albarán"] = df["Albarán"].fillna("").str.strip()

        
        df = (
            df[df["Albarán"] != ""][["Albarán"]]
            .drop_duplicates()
)

        #Eliminamos filas vacias y resetear índice
        df = df.dropna().reset_index(drop=True)
                
        return df
    except Exception as e:
        print(f"Error al leer el archivo {ruta_archivo}: {e}")
        return None 

print("\n")
fecha_inicio = input("Introducir fecha inicio (YYYY-MM-DD): ")
fecha_fin = input("Introducir fecha fin (YYYY-MM-DD): ")
while True:
    almacen = input("Elige (1) Steel o (2) Interim: ")
    if almacen == "1":
        selector_almacen = 221
        break
    if almacen == "2":
        selector_almacen = 129
        break
    else:
        print("\n Opción incorrecta, escoja 1 (Steel) o 2 (Interim)")

if selector_almacen == 221:
    nombre_almacen = "Steel"
if selector_almacen == 129:
    nombre_almacen = "Interim"

print("\n")
print("=".center(50, "="))
print("MAHOU FALTAS".center(50, "-"))
print("=".center(50, "="))
print("\n")
print(f"Procesando fechas {fecha_inicio} a {fecha_fin} para el almacén {nombre_almacen}")
print("\nComenzando con busqueda de pedidos integrados\n")
nombre_archivo = qry_pedidos_final_steel.consulta_pedidos(fecha_inicio, fecha_fin, selector_almacen)
#print(nombre_archivo)
print(f"Archivo de pedidos integrados generado")
path_file = f"{path}\\{nombre_archivo}"

print("\nComenzando descarga y lectura de EDIs\n")
df = leer_csv(path_file)
#print(df)
parsed_edis = descarga_edi_steel.descargar_edi(df, selector_almacen)
print("\nProcesado EDIs descargados\n")
#print(parsed_edis)

print("\nGenerando fichero de stock\n")
nombre_stock = qry_consulta_UBSPROD.ejecutar_qry(fecha_inicio, fecha_fin, selector_almacen)
print("\nProceso completado.\n")
#print(nombre_stock)

