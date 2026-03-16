import requests
import colorama as cl
import datetime as dt

def get_timestamp():
    year = dt.datetime.now().year
    month = dt.datetime.now().month
    day = dt.datetime.now().day +1
    hour = dt.datetime.now().hour+3
    minute = dt.datetime.now().minute

    date_time = dt.datetime(year, month, day, hour, minute)
    timestamp = int(date_time.timestamp() * 1000)

    return timestamp


cl.init()

#tiempo en milisegundos

# import time
# import datetime

# date_time = datetime.datetime(2024, 10, 3, 12, 0)
# timestamp = int(date_time.timestamp() * 1000)
# print(timestamp)  # 1727966400000


API_KEY = "4fe89196-3d2c-4aa5-b25c-0923d009d31a"
context = "ZLH5YJNENLE9TRR4P3S4OULXSZJA70B8"
udid = "057c6ad47d3647895bb3a900c44e3645"
lang = "es_ES"
internalID = "NWNTPEKJKEMLZKSPNXIYBEG6L9KSK5M7N"
url = "https://back.devarea.app/mBase/api/v3.0/turnAppointments/"

print("URL:", url)

headers = {
    "Authorization": f"bearer {API_KEY}",
    "context": context,
    "udid": udid,
    "lang": lang,
}

def tap_001_save(miliseconds):
    print("[+] TAP-001")

    body_params = {
        "turnFormInternalId": "DZLSPPKWKSGAIAOOXBFTDWI27G0TSGUUN",
        "turnDeskInternalId": "RC3WYV0DKWNTBISCI97UOOUAZR9HOZNDV",
        "appointmentDate": int(miliseconds),
        "userName": "John",
        "userSurname": "Does",
        "userDni": None,
        "userMail": None,
        "userTelephone": None,
        "userPassport": None,
        "userLicensePlate": "1111HHH"
    }

    try:
        response_API = requests.post(url, headers=headers, json=body_params, verify=False)  # Cambiar verify=False a verify=True en producción
        print(response_API.status_code)
        if response_API.status_code == 200:
            text_response = response_API.json()
            print(text_response)
        else:
            print(f"Error en la solicitud: {response_API.status_code}")
            print(response_API.text)
    except requests.RequestException as e:
        print(f"no funciona request, error: {e}")

def tap_002_delete():
    print("[+] TAP-002")
    internalID = "5CAORJZZ7MT9POE5G0NOKQP6DMTMUX7XW"
    body_params = {
        "internalId": internalID
    }

    try:
        response_API = requests.delete(url, headers=headers, json=body_params, verify=False)  # Cambiar verify=False a verify=True en producción
        print(response_API.status_code)
        if response_API.status_code == 200:
            text_response = response_API.json()
            print(text_response)
        else:
            print(f"Error en la solicitud: {response_API.status_code}")
            print(response_API.text)
    except requests.RequestException as e:
        print(f"no funciona request, error: {e}")

def tap_003_update(miliseconds):
    print("[+] TAP-003")
    internalID = "URLDSOSVTKO4CYNLXRO7ZBPVYMCKAEERI"

    body_params = {
        "appointmentInternalId": internalID,
        "turnFormInternalId": "DZLSPPKWKSGAIAOOXBFTDWI27G0TSGUUN",
        "turnDeskInternalId": "RC3WYV0DKWNTBISCI97UOOUAZR9HOZNDV",
        "appointmentDate": int(miliseconds),
        "userName": "Johnana",
        "userSurname": "Does",
        "userDni": None,
        "userMail": None,
        "userTelephone": None,
        "userPassport": None,
        "userLicensePlate": "1111HHH"
    }

    try:
        response_API = requests.put(url, headers=headers, json=body_params, verify=False)  
        print(response_API.status_code)
        if response_API.status_code == 200:
            text_response = response_API.json()
            print(text_response)
        else:
            print(f"Error en la solicitud: {response_API.status_code}")
            print(response_API.text)
    except requests.RequestException as e:
        print(f"no funciona request, error: {e}")

def tap_004_get():
    print("[+] TAP-004")
    internalID = "URLDSOSVTKO4CYNLXRO7ZBPVYMCKAEERI"
    params = {
        "internalId": internalID
    }

    try:
        response_API = requests.get(url, headers=headers, params=params, verify=False)  
        if response_API.status_code == 200:
            text_response = response_API.json()
            print(text_response)
        else:
            print(f"Error en la solicitud: {response_API.status_code}")
            print(response_API.text)
    except requests.RequestException as e:
        print(f"no funciona request, error: {e}")

def tap_005_search(url):
    print("[+] TAP-005")
    url = url + "search?"
    params = {
        "userLicensePlate": "1111HHH"
    }

    try:
        response_API = requests.get(url, headers=headers, params=params, verify=False)  # Cambiar verify=False a verify=True en producción
       
        print(response_API.status_code)
        if response_API.status_code == 200:
            text_response = response_API.json()
            print(text_response)
        else:
            print(f"Error en la solicitud: {response_API.status_code}")
            print(response_API.text)
    except requests.RequestException as e:
        print(f"no funciona request, error: {e}")

# SELECCION DE PRUEBA
try:
    while True:
        milis = get_timestamp()
        milis_backup = milis
        print("\n")
        cl.colorama_text()
        print(cl.Fore.GREEN + "[?] Seleccione opción:" + cl.Style.RESET_ALL)
        print("\n")
        print(cl.Back.BLUE + cl.Fore.RED + "\t1. TAP-001 (Save)" + cl.Style.RESET_ALL + cl.Back.BLACK)
        print(cl.Back.BLUE + cl.Fore.RED + "\t2. TAP-002 (Delete)" + cl.Style.RESET_ALL + cl.Back.BLACK)
        print(cl.Back.BLUE + cl.Fore.RED + "\t3. TAP-003 (Update)" + cl.Style.RESET_ALL + cl.Back.BLACK)
        print(cl.Back.BLUE + cl.Fore.RED + "\t4. TAP-004 (Get)" + cl.Style.RESET_ALL + cl.Back.BLACK)
        print(cl.Back.BLUE + cl.Fore.RED + "\t5. TAP-005 (Search)" + cl.Style.RESET_ALL + cl.Back.BLACK + "\n")

        opcion = int(input("[?] Su opcion (1-5):"))

        if opcion == 1:
            tap_001_save(milis)
        elif opcion == 2:
            tap_002_delete()
        elif opcion == 3:
            tap_003_update(milis_backup)
        elif opcion == 4:
            tap_004_get()
        elif opcion == 5:
            tap_005_search(url)
        else:
            print("[!] Opción no válida. Inténtelo de nuevo.") 

except KeyboardInterrupt:
    print("\n[!] Saliendo...")
