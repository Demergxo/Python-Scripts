def arbol_navidad(niveles):
    for i in range(niveles):
        espacios = " " * (niveles - i - 1)
        asteriscos = "*" * (2 * i + 1)
        print(espacios + asteriscos)

def tronco(niveles):
    espacios_tronco = " " * (niveles - 1)
    print(espacios_tronco + "|\n")

def main():
    try:
        niveles = int(input("Ingrese el número de niveles del árbol de Navidad: "))
        print("")
        if niveles <= 0:
            raise ValueError("El número de niveles debe ser un entero positivo.")
        
        arbol_navidad(niveles)
        tronco(niveles)

    except ValueError as e:
        print(f"Error: {e}. Por favor, ingrese un número entero positivo.")

if __name__ == "__main__":
    main()

