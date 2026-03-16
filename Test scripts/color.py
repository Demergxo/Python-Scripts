from colorama import init, Fore, Back, Style

init()

print(Fore.RED+"Texto en rojo")
print(Style.BRIGHT+"Texto claro")
print(Back.BLUE+Fore.RED+"Cambio")
