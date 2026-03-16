import praw
import requests
import os
import ssl

ssl._create_default_https_context = ssl._create_unverified_context
# Configuración de la API de Reddit
reddit = praw.Reddit(
    client_id='ngdjOU166CwCTyDxxFO2JA',
    client_secret='	WIqHxtO4C5wsh3ngVXrfVUJ1LQtAxAT',
    user_agent='script_imagen_diaria',
)

# Subreddit para obtener imágenes (puedes cambiarlo según lo que busques)
#Art, Animeart, NSFW, EarthPorn
subreddit_name = 'Art'  # Ejemplo: paisajes
output_folder = 'imagenes_diarias'

# Asegúrate de que exista la carpeta de destino
os.makedirs(output_folder, exist_ok=True)

def descargar_imagen(subreddit_name):
    subreddit = reddit.subreddit(subreddit_name)
    for submission in subreddit.hot(limit=10):  # Buscar las imágenes más populares
        if submission.url.endswith(('.jpg', '.png')):
            file_name = os.path.join(output_folder, f"{submission.id}.jpg")
            if not os.path.exists(file_name):
                response = requests.get(submission.url)
                if response.status_code == 200:
                    with open(file_name, 'wb') as f:
                        f.write(response.content)
                    print(f"Imagen descargada: {file_name}")
                    return  # Solo descargar una imagen
    print("No se encontraron imágenes.")

# Ejecutar el script
descargar_imagen(subreddit_name)
