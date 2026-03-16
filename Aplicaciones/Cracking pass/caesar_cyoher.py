def select():
    mensaje = input("\nEscriba mensaje: ")

    select_mode = int(input("\nEscriba '1' para cifrar, '2' para descifrar o '3' para salir(1/2/3): "))

    if select_mode == 1:
        mode = "encrypt"
    elif select_mode == 2:
        mode = "decrypt"
    elif select_mode == 3:
        exit()
    else:
        print("Entrada inválida.")
    
    while True:  
        try:
            key = int(input("\nEscriba la llave (número): "))
            break
        except ValueError:
            print("Entrada inválida. Inténtelo de nuevo.")
        
    return mensaje, mode, key

def cypher(mensaje, mode, key):

    SYMBOLS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz1234567890 !?.`~@#$%^&*()_+-=[]{}|;:<>,/'

    translated = ''

    for symbol in mensaje:
        if symbol in SYMBOLS:
            symbolIndex = SYMBOLS.find(symbol)
            if mode == 'encrypt':
                translatedIndex = symbolIndex + key
            elif mode == 'decrypt':
                translatedIndex = symbolIndex - key
            if translatedIndex >= len(SYMBOLS):
                translatedIndex = translatedIndex - len(SYMBOLS)
            elif translatedIndex < 0:
                translatedIndex = translatedIndex + len(SYMBOLS)
            translated = translated + SYMBOLS[translatedIndex]
        else:
            translated = translated + symbol
    return translated

try:
    while True:
        mensaje, mode, key = select()
        translated = cypher(mensaje, mode, key)
        print("\nEl mensaje cifrado es:", translated)
        print("\n")
        
except KeyboardInterrupt:
    print("\nSaliendo...")

        
