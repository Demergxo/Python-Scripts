import socket

def check_port(host, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(3)  # tiempo de espera en segundos

    try:
        sock.connect((host, port))
        return True
    except socket.error:
        return False
    finally:
        sock.close()

def main():
    host = input("Introduce la dirección IP o el nombre del host: ")

    # Lista de puertos comunes que puedes personalizar según tus necesidades
    ports_to_check = [20, 21, 22, 25, 53, 80, 123, 179, 443, 500, 587,3306, 3389, 8080, 8443, 8081, 8082, 8083, 8084, 8085, 8086, 8087, 8088, 8089, 8090, 8091, 8092, 8093, 8094, 8095, 8096, 8097, 8098, 8099, 8100, 8888]

    print(f"\nComprobando el estado de los puertos en {host}:\n")

    for port in ports_to_check:
        if check_port(host, port):
            print(f"Puerto {port} está abierto")
        else:
            print(f"Puerto {port} está cerrado")

if __name__ == "__main__":
    main()
