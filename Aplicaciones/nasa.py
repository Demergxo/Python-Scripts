import requests
from alive_progress import alive_bar #type:ignore
import json

a = 1

with alive_bar(a) as bar:  # default setting
    for i in range(a):
        api_url = "https://api.nasa.gov/planetary/apod?api_key=HGT0eyvXKBWNRkl51KpjfKkiJLWaXQimW8PIfVLn"

        # Añadir encabezados
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:133.0) Gecko/20100101 Firefox/133.0"
        }

        request = requests.get(api_url, headers=headers)#, verify=False)#proxies=proxies,

        print("*" * 32)
        print(f"\nStatus: {request.status_code} \n")
        print("*" * 32 + "\n")
        if request.status_code == 200:
            text_response = request.json()
            print(json.dumps(text_response, indent=4))
            print("\n" + "*" * 32)
        else:
            print("Status with error")
            print(request.text)  # Imprime el mensaje de error del servidor

        bar()