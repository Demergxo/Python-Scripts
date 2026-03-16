from sympy import true


def kinetic_energy(mass, velocity):
    return 0.5 * mass * velocity**2

def calcular_celsius_fahrenheit(celsius):
    return (celsius * 9/5) + 32

def calcular_fahrenheit_celsius(fahrenheit):
    return (fahrenheit - 32) * 5/9

def calcular_velocidad_caida_cuerpo(gravedad, tiempo):
    return gravedad * tiempo

def convertir_temperaturas():
    seleccion = input("¿Desea convertir de Celsius a Fahrenheit o viceversa? (C/F): ").upper()
    if seleccion == 'C':
        try:
            celsius = float(input("Ingrese la temperatura en Celsius: "))
            resultado = calcular_celsius_fahrenheit(celsius)
            print(f"{celsius}°C es igual a {resultado}°F")
        except ValueError:
            print("Entrada inválida. Por favor, ingrese un número válido.")
    elif seleccion == 'F':
        try:
            fahrenheit = float(input("Ingrese la temperatura en Fahrenheit: "))
            resultado = calcular_fahrenheit_celsius(fahrenheit)
            print(f"{fahrenheit}°F es igual a {resultado}°C")
        except ValueError:
            print("Entrada inválida. Por favor, ingrese un número válido.")
    else:
        print("Opción inválida")

def calcular_energia_cinetica():
    try:
        mass = float(input("Ingrese la masa del objeto (en kg): "))
        velocity = float(input("Ingrese la velocidad del objeto (en m/s): "))
        resultado = kinetic_energy(mass, velocity)
        print(f"La energía cinética del objeto es: {resultado} J")
    except ValueError:
        print("Entrada inválida. Por favor, ingrese números válidos.")

def calcular_velocidad_caida():
    try:
        gravedad_input = input("Ingrese la aceleración de la gravedad (en m/s^2) (por defecto 9.8): ")
        gravedad = float(gravedad_input) if gravedad_input else 9.8
        tiempo = float(input("Ingrese el tiempo en segundos: "))
        resultado = calcular_velocidad_caida_cuerpo(gravedad, tiempo)
        print(f"La velocidad de caída del objeto es: {resultado} m/s")
    except ValueError:
        print("Entrada inválida. Por favor, ingrese números válidos.")

def salida():
    print("¡Hasta luego!")
    exit()

def seleccion_de_utilidad(valor):
    opciones = {
        1: convertir_temperaturas,
        2: calcular_energia_cinetica,
        3: calcular_velocidad_caida,
        4: salida,
    }
    # Si valor no está en opciones, usa la lambda para imprimir "Opción inválida"
    funcion = opciones.get(valor, lambda: print("Opción inválida"))
    funcion()

def main():
    while True:
        print("\nSeleccione una opción:")
        print("\n1: Convertir temperaturas (Celsius/Fahrenheit)")
        print("2: Calcular energía cinética de un objeto")
        print("3: Calcular velocidad de caída de un objeto")
        print("4: Salir\n")
        try:
            opcion = int(input("Ingrese el número de la opción deseada: "))
            seleccion_de_utilidad(opcion)
        except ValueError:
            print("Entrada inválida. Por favor, ingrese un número válido.")

if __name__ == "__main__":
    main()
