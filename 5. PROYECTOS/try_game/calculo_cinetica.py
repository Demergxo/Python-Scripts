

def kinetic_energy(mass, velocity):
    # Calcula la energía cinética de un cuerpo en movimiento en un plano
    kinetic_energy = 0.5 * mass * velocity**2
    return kinetic_energy

def calcular_celsius_fahrenheit(celsius):
    #Calcula la temperatura de centigrados a fahrenheit
    fahrenheit = (celsius * 9/5) + 32
    return fahrenheit

def calcular_fahrenheit_celsius(fahrenheit):
    #Calcula la temperatura de fahrenheit a centigrados
    celsius = (fahrenheit - 32) * 5/9
    return celsius
def calcular_velocidad_caida_cuerpo(gravedad, tiempo):
    #Calcula la velocidad de caída de un cuerpo
    velocidad_caida = gravedad * tiempo
    return velocidad_caida

def seleccion_de_utilidad(valor):
    if valor == 1:
        seleccion = input("¿Desea convertir de Celsius a Fahrenheit o viceversa? (C/F): ")
        if seleccion.upper() == 'C':
            celsius = float(input("Ingrese la temperatura en Celsius: "))
            resultado = calcular_celsius_fahrenheit(celsius)
            print(f"{celsius}°C es igual a {resultado}°F")
        elif seleccion.upper() == 'F':
            fahrenheit = float(input("Ingrese la temperatura en Fahrenheit: "))
            resultado = calcular_fahrenheit_celsius(fahrenheit)
            print(f"{fahrenheit}°F es igual a {resultado}°C")
        else:
            print("Opción inválida")
    elif valor == 2:
        print("Este programa calcula la energía cinética de un objeto")
        mass = float(input("Ingrese la masa del objeto (en kg): "))
        velocity = float(input("Ingrese la velocidad del objeto (en m/s): "))

        resultado = kinetic_energy(mass, velocity)
        print(f"La energía cinética del objeto es: {resultado} J")
    elif valor == 3:
        print("Este programa calula la velocidad de caida de un objeto")
        gravedad = float(input("Ingrese la aceleración de la gravedad (en m/s^2)(por defecto 9,8): "))
        if gravedad == "":
            gravedad = 9.8
        tiempo = float(input("Ingrese el tiempo en segundos: "))
        resultado = calcular_velocidad_caida_cuerpo(gravedad, tiempo)
        print(f"La velocidad de caída del objeto es: {resultado} m/s")
    else:
        return "Opción inválida"


def main():
    print("Seleccione una opción:")
    print("1: Convertir temperaturas (Celsius/Fahrenheit)")
    print("2: Calcular energía cinética de un objeto")
    print("3: Calcular velocidad de caída de un objeto")
    try:
        opcion = int(input("Ingrese el número de la opción deseada: "))
        seleccion_de_utilidad(opcion)
    except ValueError:
        print("Entrada inválida. Por favor, ingrese un número válido.")

if __name__ == "__main__":
    main()




