import os
import platform
import psutil

def obtener_info_sistema():
    sistema_operativo = platform.system()
    arquitectura = platform.architecture()
    try:
        win_edit = platform.win32_edition()
    except AttributeError:
        win_edit = "No disponible"
    memoria = psutil.virtual_memory()
    disco = psutil.disk_usage('/')
    num_cpus = os.cpu_count()
    #procesos = sorted(psutil.process_iter(), key=lambda x: x.memory_info().rss, reverse=True)
    procesador= platform.processor()
    release = platform.release()
    machine = platform.machine()
    node_name = platform.node()
    tecnic = platform.platform()
    version_os = platform.version()
    usuario = os.environ['USERNAME']

    return sistema_operativo, arquitectura, memoria, disco, num_cpus, procesador, release, machine, node_name, win_edit, tecnic, version_os, usuario, #procesos

def bytes_a_gb(bytes_valor):
    gb_valor = bytes_valor / (1024 ** 3)  # 1 GB = 1024^3 bytes
    return gb_valor

def mostrar_info_sistema(info):
    sistema_operativo, arquitectura, memoria, disco, num_cpus, procesador, release, machine, node_name, alias_so, tecnic, version_os, usuario = info #procesos

    print("Información del sistema:")
    print("*"*24)
    print("\nSistema Operativo: {}".format(sistema_operativo))
    print("Release: {}".format(release))
    print("Nombre Técnico: {}".format(tecnic))
    print("Arquitectura: {}".format(arquitectura))
    print("Tipo comercial: {}".format(alias_so))
    print("Versión: {}".format(version_os))
    print("\nProcesador: {}".format(procesador))
    print("Tipo de máquina: {}".format(machine))
    print("Numero de CPU's: {}".format(num_cpus))
    print("\nMemoria Total: {:.2f} GB".format(bytes_a_gb(memoria.total)))
    print("Uso de Memoria: {:.2f} GB".format(bytes_a_gb(memoria.used)))
    print("Porcentaje de Uso de Memoria: {}% \n".format(memoria.percent))
    print("Espacio Total en Disco: {:.2f} GB".format(bytes_a_gb(disco.total)))
    print("Espacio Usado en Disco: {:.2f} GB".format(bytes_a_gb(disco.used)))
    print("Porcentaje de Uso de Disco: {}% \n".format(disco.percent))
    print("Usuario: {}".format(usuario))
    
    # try:
    #     proceso_mas_consumidor = procesos[0]
    #     consumo_memoria = proceso_mas_consumidor.memory_info().rss
    
    #     print("\nProceso que más consume memoria:")
    #     print("*"*32)
    #     print("\nNombre: {}".format(proceso_mas_consumidor.name()))
    #     print("PID: {}".format(proceso_mas_consumidor.pid))
    #     print("Consumo de Memoria: {:.2f} MB".format(consumo_memoria / (1024 ** 2)))
    # except:
    #     print("\n Actualmente no podemos mostrar el proceso que más consume")
    
    print("\nDatos especificos de la máqina:")
    print("*"*31)
    print("Nombre del host: {}".format(node_name))
if __name__ == "__main__":
    info_sistema = obtener_info_sistema()
    mostrar_info_sistema(info_sistema)

