import subprocess
import platform
import ipaddress
import socket
import re

def ping_ip(ip):
    # Determina el comando de ping según el sistema operativo
    param = "-n" if platform.system().lower() == "windows" else "-c"
    command = ["ping", param, "1", str(ip)]
    
    try:
        # Ejecuta el comando de ping y obtiene el resultado
        output = subprocess.check_output(command, stderr=subprocess.STDOUT).decode('latin-1')
        ttl = extract_ttl(output)
        return True, ttl
    except subprocess.CalledProcessError:
        return False, None

def extract_ttl(ping_output):
    # Busca el valor TTL en la salida del comando ping
    ttl_search = re.search(r"TTL=(\d+)", ping_output, re.IGNORECASE)
    if ttl_search:
        return int(ttl_search.group(1))
    return None

def guess_os(ttl):
    if ttl is None:
        return "Desconocido"
    elif ttl >= 128:
        return "Windows"
    elif ttl >= 64:
        return "Linux/Unix"
    elif ttl >= 32:
        return "Router/Embedded"
    else:
        return "Desconocido"

def get_hostname(ip):
    try:
        # Obtiene el nombre del host para la IP dada
        hostname = socket.gethostbyaddr(ip)[0]
    except socket.herror:
        hostname = None
    return hostname

def check_ip_range(network):
    net = ipaddress.ip_network(network, strict=False)
    
    available_ips = []
    occupied_ips = {}
    
    for ip in net.hosts():
        ip_str = str(ip)
        is_occupied, ttl = ping_ip(ip_str)
        if is_occupied:
            hostname = get_hostname(ip_str)
            os_type = guess_os(ttl)
            occupied_ips[ip_str] = {"hostname": hostname, "os": os_type}
        else:
            available_ips.append(ip_str)
    
    gateway = str(next(net.hosts()))  # Supone que la primera IP después de la dirección de red es la puerta de enlace
    broadcast = str(net.broadcast_address)
    
    return available_ips, occupied_ips, gateway, broadcast

# Ejemplo de uso:
network = "10.59.128.0/28"
available_ips, occupied_ips, gateway, broadcast = check_ip_range(network)

print(f"Las siguientes IPs están libres en la red {network}:")
for ip in available_ips:
    print(ip)

print(f"\nLas siguientes IPs están ocupadas en la red {network}:")
for ip, info in occupied_ips.items():
    hostname = info["hostname"] if info["hostname"] else "Nombre de host no encontrado"
    os_type = info["os"]
    print(f"{ip} - {hostname} - {os_type}")

print(f"\nLa puerta de enlace predeterminada es: {gateway}")
print(f"La dirección de broadcast es: {broadcast}")
