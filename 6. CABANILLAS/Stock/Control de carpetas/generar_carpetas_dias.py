import os
from datetime import datetime, timedelta

def crear_carpetas(year, month, ruta):
    # Obtener el número de días en el mes y año dados
    num_dias = obtener_dias_en_mes(year, month)
    
    # Crear las carpetas
    for dia in range(1, num_dias + 1):
        fecha = datetime(year, month, dia)
        formato_fecha = fecha.strftime("%Y-%m-%d")
        nueva_ruta = os.path.join(ruta, formato_fecha)
        
        # Crear la carpeta si no existe
        if not os.path.exists(nueva_ruta):
            os.makedirs(nueva_ruta)
            print(f'[+] Carpeta creada: {nueva_ruta}')
        else:
            print(f'[!] Carpeta ya existe: {nueva_ruta}')

def obtener_dias_en_mes(year, month):
    # Calcula el número de días en el mes y año dados
    if month == 12:
        next_month = 1
        next_year = year + 1
    else:
        next_month = month + 1
        next_year = year
    
    # Primer día del próximo mes
    primer_dia_siguiente_mes = datetime(next_year, next_month, 1)
    
    # Último día del mes actual
    ultimo_dia_mes_actual = primer_dia_siguiente_mes - timedelta(days=1)
    
    return ultimo_dia_mes_actual.day

def main():
    # Solicitar al usuario el año y el mes
    year = int(input("[?] Ingrese el año (ej. 2024): "))
    month = int(input("[?] Ingrese el mes (ej. 7 para julio): "))
    
    # Solicitar la ruta donde se crearán las carpetas
    ruta = input("[?] Ingrese la ruta donde desea crear las carpetas: ")
    
    # Llamar a la función para crear las carpetas
    crear_carpetas(year, month, ruta)

if __name__ == "__main__":
    main()
