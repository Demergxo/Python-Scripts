import os
import datetime as dt

year = dt.datetime.now().year

def initial():
    try:
        path = input("[?] Introduzca ruta: ")
        year = input("[?] Introduzca el año: ")
    
        path = path + "\\" + f"PLANTILLAS INVENTARIOS ROTATIVOS {year}" + "\\"


        print(f"[+] La ruta es: {path}")
        decision = input("[?] Es correcto? (S (si)/N (no)/E (salir)): ")
    
    
        return path, decision
    except KeyboardInterrupt:
        print("\n\n[!] Saliendo... \n\n")
        exit(0)

def meses(path):
    meses = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
    num = 1
    os.makedirs(path, exist_ok=True)
    for num, mes in enumerate(meses,1):
        
        path_full = os.path.join(path, f"{str(num).zfill(2)}. {mes}")
        print(path_full)

        os.makedirs(path_full, exist_ok=True)


listElux = ["01. ANALISIS ABC", "02. ARCHIVO JC PRUEBAS", "03. AJUSTE W Y SOBRANTES", "04. Cycle Count ELECTROLUX", "05. CONTROL ID. CARGAS - DESCARGAS TEAM SITE", "06. DOCUMENTACION", "07. MANUALES", "08. MASTER MATERIAL", "09. REPORTE ERRORES", "10. PLANTILLAS", "11. PROYECTOS - TEST", "12. DISCREPANCIAS", "13. UBIS. VACIAS PARA CONTROL", "13.B. UBIS. CABECEROS Y X", "14. Inventario Profesional", "15. Layout BULK QR", "16. BACKUP", "17. IMPLANTACIONES"]

directory_cwd = os.getcwd()


print("El directorio actual es: ")
print(directory_cwd)
print("")


try: 
    while True:
        num = 1
        path, dec = initial() 
        
        if dec.lower() == "s":
            os.makedirs(path, exist_ok=True)
            for carpeta in listElux:
                
                path_full = path + carpeta 
                print(path_full)
                num = num + 1
                os.makedirs(path_full, exist_ok=True)
                
                if carpeta == "06. DOCUMENTACION":
                    subdirs = ["01. Auditorias Cargas", "02. Auditorias Descargas"]
                    for subdir in subdirs:
                        path_subdir = os.path.join(path_full, subdir)
                        os.makedirs(path_subdir, exist_ok=True)
                        meses(path_subdir)
        elif dec.lower() == "n":
            print("[!] Probemos de nuevo")
        elif dec.lower() == "e":
            print("[+] Hasta luego!!")
            break
        else:
            print("[!] Opción incorrecta")
except KeyboardInterrupt:
    print("\n\n[+] Saliendo del programa... \n\n")
    exit(0)