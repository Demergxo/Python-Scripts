import subprocess
import winsound  # Para hacer sonar una alerta
import time

# Lista de usuarios permitidos (puedes editar esto con los usuarios válidos en tu sistema)
usuarios_permitidos = [">jgmeras"]

def obtener_usuarios_activos():
    try:
        resultado = subprocess.check_output('quser', shell=True, text=True)
        lineas = resultado.strip().splitlines()[1:]  # Saltar encabezado
        usuarios_activos = []

        for linea in lineas:
            partes = linea.split()
            if "Activo" in partes:
                usuario = partes[0]
                usuarios_activos.append(usuario)

        return usuarios_activos

    except subprocess.CalledProcessError as e:
        print("Error al ejecutar 'quser':", e)
        return []

def revisar_usuarios():
    activos = obtener_usuarios_activos()
    print("Usuarios activos:", activos)

    for usuario in activos:
        if usuario not in usuarios_permitidos:
            print(f"⚠️ ALERTA: Usuario no autorizado detectado -> {usuario}")
            winsound.Beep(1000, 800)  # Beep fuerte para alertar
        else:
            print(f"✔️ Usuario autorizado: {usuario}")

# Puedes ejecutar esto una vez o en un bucle cada cierto tiempo
if __name__ == "__main__":
    revisar_usuarios()
    # O descomenta esto si quieres que revise cada 60 segundos
    # while True:
    #     revisar_usuarios()
    #     time.sleep(60)
