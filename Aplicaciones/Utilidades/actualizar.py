import subprocess
import sys
import signal


def signal_handler(sig, frame):
    print('\nActualización cancelada.')
    sys.exit(1)
    
signal.signal(signal.SIGINT, signal_handler)

def actualizar_librerias():
    try:
        # Obtener la lista de paquetes instalados
        paquetes = subprocess.check_output([sys.executable, '-m', 'pip', 'freeze'])
        paquetes = paquetes.decode('utf-8').splitlines()
        paquetes = [p.split('==')[0] for p in paquetes]
        
        # Actualizar cada paquete
        for paquete in paquetes:
            print(f'Actualizando {paquete}...')
            try:
                subprocess.run([sys.executable, '-m', 'pip', 'install', '--upgrade', paquete, '--no-warn-script-location'], check=True)
            except Exception as error:
                print(f"Fallo en libreria: {error}")
                pass
    except Exception as e:
        print(f'Error durante la actualización: {e}')
    finally:
        print('\nScritp completado.')

if __name__ == "__main__":
    actualizar_librerias()
