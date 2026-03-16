import os

def initial():
    try:
        path = input("[?] Introduzca ruta: ")
        year = input("[?] Introduzca el año: ")
    
        path = path + "\\" + year + "\\"


        print(f"[+] La ruta es: {path}")
        decision = input("[?] Es correcto? (S (si)/N (no)/E (salir)): ")
    
    
        return path, decision
    except KeyboardInterrupt:
        print("\n\n[!] Saliendo... \n\n")
        exit(0)
        




meses = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]

directory_cwd = os.getcwd()


print("El directorio actual es: ")
print(directory_cwd)
print("")


try: 
    while True:
        num = 1
        path, dec = initial() 
        #print(dec.lower())
        if dec.lower() == "s":
            os.makedirs(path, exist_ok=True)
            for mes in meses:
                
                path_full = path + str(num).zfill(2) + ". " + mes
                print(path_full)
                num = num + 1
                os.makedirs(path_full, exist_ok=True)
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


