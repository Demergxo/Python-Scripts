def main():
    try:
    
        mensaje = input("\n[?] Ingrese el mensaje a cifrar: ")
        while True:
            try:
                key = int(input("[?] Ingrese la llave (número): "))
                break
            except ValueError:
                print("\n[!] Entrada inválida. Inténtelo de nuevo.\n")
        
        texto_cifrado = cifrar_mensaje(mensaje, key)
        print("\n"+texto_cifrado + "|\n")
    except KeyboardInterrupt:
        print("\nSaliendo...")
    
def cifrar_mensaje(mensaje, key):
    texto_cifrado = ['']*key
    for columna in range(key):
        indice = columna
        while indice < len(mensaje):
            texto_cifrado[columna] += mensaje[indice]
            indice += key
    return ''.join(texto_cifrado)

if __name__ == "__main__":
    main()
 