import ipaddress
import socket
from scapy.all import ARP, Ether, srp, ICMP, IP, sr1 #type: ignore

def escanear_red(direccion_red, modificador):
    # Crear objeto de red con el modificador proporcionado
    red = ipaddress.ip_network(f"{direccion_red}/{modificador}", strict=False)
    
    # Crear paquete ARP para la transmisión
    paquete = Ether(dst="ff:ff:ff:ff:ff:ff") / ARP(pdst=str(red))
    
    # Enviar paquete y recibir respuestas
    resultado = srp(paquete, timeout=2, verbose=0)[0]
    
    # Diccionario para almacenar dispositivos encontrados
    dispositivos = {}
    
    # Iterar sobre las respuestas
    for _, recibido in resultado:
        ip = recibido.psrc
        mac = recibido.hwsrc
        hostname = obtener_hostname(ip)
        ttl = obtener_ttl(ip)
        sistema_operativo = estimar_sistema_operativo(ttl)
        dispositivos[ip] = {
            "MAC": mac,
            "Hostname": hostname,
            "TTL": ttl,
            "Sistema Operativo": sistema_operativo
        }
    
    # Listar IPs en la red
    todas_ips = list(red.hosts())
    
    # IPs libres son aquellas que no están en los dispositivos encontrados
    ips_libres = [str(ip) for ip in todas_ips if str(ip) not in dispositivos]
    
    return dispositivos, ips_libres

def obtener_hostname(ip):
    try:
        hostname = socket.gethostbyaddr(ip)[0]
    except socket.herror:
        hostname = "Desconocido"
    return hostname

def obtener_ttl(ip):
    # Enviar paquete ICMP (ping) para obtener el TTL
    paquete = IP(dst=ip) / ICMP()
    respuesta = sr1(paquete, timeout=1, verbose=0)
    if respuesta:
        return respuesta.ttl
    else:
        return None

def estimar_sistema_operativo(ttl):
    # Estimar sistema operativo basado en el valor de TTL
    if ttl is None:
        return "Desconocido"
    elif ttl <= 64 and ttl > 128:
        return "Linux/Unix"
    elif ttl <= 128 and  ttl > 255:
        return "Windows"
    elif ttl <= 255:
        return "Cisco/Router"
    else:
        return "Desconocido"

def mostrar_resultados(dispositivos, ips_libres):
    print("Dispositivos encontrados en la red:")
    for ip, info in dispositivos.items():
        print(f"IP: {ip}, MAC: {info['MAC']}, Hostname: {info['Hostname']}, TTL: {info['TTL']}, Sistema Operativo: {info['Sistema Operativo']}")
    
    print("\nIPs libres en la red:")
    for ip in ips_libres:
        print(ip)

if __name__ == "__main__":
    # Dirección de red y modificador de bytes
    direccion_red = "10.59.33.0"
    modificador = 24
    
    # Escanear la red
    dispositivos, ips_libres = escanear_red(direccion_red, modificador)
    
    # Mostrar los resultados
    mostrar_resultados(dispositivos, ips_libres)
