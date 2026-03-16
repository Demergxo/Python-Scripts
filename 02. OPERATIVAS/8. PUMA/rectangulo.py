from re import T
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

def draw_3d_rectangle(height, width, length):
    # Crea un nuevo gráfico 3D
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    # Define las esquinas del rectángulo
    r = [0, length]  # x-coordinates
    X, Y = np.meshgrid(r, r)  # meshgrid for creating the rectangle

    # Define las caras del rectángulo
    ax.scatter3D(X, Y, 0, color='b', alpha=0.5)  # Bottom face
    ax.scatter3D(X, Y, height, color='r', alpha=0.5)  # Top face

    # Lados del rectángulo
    ax.plot_surface(X, 0, Y, color='cyan', alpha=0.5)
    ax.plot_surface(X, height, Y, color='magenta', alpha=0.5)
    ax.plot_surface(0, X, Y, color='yellow', alpha=0.5)
    ax.plot_surface(length, X, Y, color='green', alpha=0.5)

    # Etiquetas de los ejes
    ax.set_xlabel('Length')
    ax.set_ylabel('Width')
    ax.set_zlabel('Height')

    # Establece los límites de los ejes
    ax.set_xlim([0, length])
    ax.set_ylim([0, width])
    ax.set_zlim([0, height])

    # Muestra el gráfico
    plt.show()
    

#depth, width, height
print("\nIntroduce las dimensiones del rectángulo:\n")

try:
    try:
        while True:
            # Solicita al usuario que ingrese las dimensiones del rectángulo
            height = float(input("Altura: "))
            width = float(input("Ancho: "))
            depth = float(input("Largo: "))

            # Dibuja el rectángulo en 3D
            draw_3d_rectangle(height, width, depth)

            # Pregunta al usuario si desea ingresar otro rectángulo
            answer = input("\n¿Deseas ingresar otro rectángulo? (s/n): ")
            if answer.lower() != 's':
                break
    except ValueError:
        print("Por favor, introduce un valor numérico válido.")
except KeyboardInterrupt:
    print("\n\n[!] Saliendo...\n")
    exit()  # Salir del programa si se presiona Ctrl+C

draw_3d_rectangle(height, width, depth)
