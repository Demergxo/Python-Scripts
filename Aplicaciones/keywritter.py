import pyautogui
import time

def escribir_en_pantalla(texto):
    # Espera unos segundos para que puedas cambiar al lugar donde quieres escribir
    time.sleep(5)
    
    # Simula escribir el texto en la pantalla
    pyautogui.typewrite(texto)
    
    # Presiona la tecla Enter
    pyautogui.press('enter')

if __name__ == "__main__":
    texto_a_escribir = "Hola, esto es un mensaje predefinido de script de Python."

    print("El script comenzará en 5 segundos. Cambia al lugar donde quieres escribir.")
    escribir_en_pantalla(texto_a_escribir)
