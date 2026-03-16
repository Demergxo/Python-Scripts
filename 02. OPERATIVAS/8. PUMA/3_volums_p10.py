from math import e
import random
from alive_progress import alive_bar

from alive_progress import animations



def calcular_dimensiones(volumen_dm3):
    bar = animations.bar_factory('🛠️', tip="🔨", background='💡', borders=('Trabajando 👉 ->|','|<- Terminado 🤘'), errors=('<---👀', '💀'))
    # Convertir el volumen a cm³ (1 dm³ = 1000 cm³)
    volumen_objetivo_cm3 = volumen_dm3 * 1000 * 0.18

    combinaciones = []

    # Generar 3 combinaciones de dimensiones
    total = 3
    i= 0
    with alive_bar(total, title='Calculando', spinner ='twirls', bar = bar) as bar:
        while i < total:
            # Generar una dimensión base y variaciones pequeñas para mantener homogeneidad
            base = (volumen_objetivo_cm3 ** (1/3))  # Aproximadamente la raíz cúbica del volumen objetivo

            # Crear ligeras variaciones para las tres dimensiones alrededor del valor base
            alto = base * random.uniform(0.9, 1.1)
            ancho = base * random.uniform(0.9, 1.1)
            profundo = base * random.uniform(0.9, 1.1)

            # Ajustar proporcionalmente para que el producto de alto, ancho y profundo sea el volumen objetivo
            factor_ajuste = (volumen_objetivo_cm3 / (alto * ancho * profundo)) ** (1/3)
            alto *= factor_ajuste
            ancho *= factor_ajuste
            profundo *= factor_ajuste

            combinaciones.append((alto, ancho, profundo))
            bar()  # Actualiza la barra de progreso.
            i += 1  # Incrementa el contador.

        return combinaciones


#volumen_total_dm3 = 22.8  # Volumen total en dm³ que deseas ingresar

try:
    while True:
        # Solicitar al usuario que ingrese el volumen total en dm³
        try:
            volumen_total_dm3 = float(input("\nIngresa el volumen total en dm³ que deseas ingresar: "))
            
            print("\n")
            print("*"*32)
            print("\n")
            combinaciones = calcular_dimensiones(volumen_total_dm3)

            for i, (alto, ancho, profundo) in enumerate(combinaciones, start=1):
                volumen_calculado = alto * ancho * profundo
                print(f"Combinación {i}: Alto = {alto:.2f} cm, Ancho = {ancho:.2f} cm, Profundo = {profundo:.2f} cm")
                #print(f"Volumen calculado: {volumen_calculado:.2f} cm³ (esperado: {volumen_total_dm3 * 1000 * 0.18:.2f} cm³)\n")
            print("\n")

        except ValueError:
            print("Por favor, ingresa un valor numérico válido.")
            #exit()  # Salir del programa si el valor no es numérico
except KeyboardInterrupt:
    print("\n\n[!] Saliendo...\n")
    exit()  # Salir del programa si se presiona Ctrl+C
    

