def pixels_to_cm(pixels, ppi):
    # Convertir píxeles a cm
    cm = (pixels / ppi) * 2.54
    return cm

def cm_to_pixels(cm, ppi):
    # Convertir cm a píxeles
    pixels = (cm / 2.54) * ppi
    return pixels


#ppi = 96  # Cambia esto según la resolución de la pantalla
#pixels = 300
#cm = 10

try:
    while True:
        # Conversión de píxeles a cm
        print("\nSeleccione una opcion:\n")
        print("\t1. Convertir píxeles a cm")
        print("\t2. Convertir cm a píxeles")

        seleccion = input("\nIngrese una opcion: ")
        if seleccion == "1":
            pixels = float(input("Ingrese la cantidad de píxeles: "))
            ppi = float(input("Ingrese la resolución de la pantalla (PPI) (96 para monitores normales, 300 para smartphones): "))
            cm_result = pixels_to_cm(pixels, ppi)
            print(f"{pixels} píxeles son {cm_result:.2f} cm a {ppi} PPI.")
            salir = input("\n¿Desea salir? (s/n): ")
            if salir.lower() == "s":
                print("\n[!] Saliendo...\n")
                break
        elif seleccion == "2":
            cm = float(input("Ingrese la cantidad de cm: "))
            ppi = float(input("Ingrese la resolución de la pantalla (PPI) (96 para monitores normales, 300 para smartphones): "))
            pixels_result = cm_to_pixels(cm, ppi)
            print(f"{cm} cm son {pixels_result:.2f} píxeles a {ppi} PPI.")
            salir = input("\n¿Desea salir? (s/n): ")
            if salir.lower() == "s":
                print("\n[!] Saliendo...\n")
                break
        else:
            print("Opción no válida. Por favor, seleccione 1 o 2.")
except KeyboardInterrupt:
    print("\n\n[!] Saliendo...\n")
    exit()  # Salir del programa si se presiona Ctrl+C

