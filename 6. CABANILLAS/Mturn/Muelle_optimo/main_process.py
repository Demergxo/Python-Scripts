import subprocess
import multiprocessing
import pyfiglet




# Función que ejecuta un script de Python
def run_script(script_path):
    result = subprocess.run(['python', 'bot_zoo_transp.py'], capture_output=True, text=True)
    print(f"Output of {script_path}:")
    print(result.stdout)
    
# Lista de scripts que se van a ejecutar en paralelo
scripts = ['bot_zoo_transp.py', 'main.py']


# Crear un Pool de procesos y ejecutar los scripts en paralelo
if __name__ == "__main__":
    result = pyfiglet.figlet_format("MUELLE", font="isometric2")
    print(result)
    result = pyfiglet.figlet_format("OPTIMO", font="isometric2")
    print(result)
    with multiprocessing.Pool(processes=len(scripts)) as pool:
        pool.map(run_script, scripts)

    print("All scripts have finished execution")
