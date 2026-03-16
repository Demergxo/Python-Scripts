import requests
from requests.auth import HTTPBasicAuth
from alive_progress import alive_bar
import json

# TAP-001 (SAVE)        
response_API = requests.get("https://admin.mbase.app/mBase/api/v3.0/turnAppointments")


API_KEY = "bearer bbb15567-5a38-425d-8d67-313e69117bc3"
context = "F0EIDJM819GB19ZJQUW3Z467D3AXVM693"
#udid = "057c6ad47d3647895bb3a900c44e3645"
lang = "es_ES"
params = "NWNTPEKJKEMLZKSPNXIYBEG6L9KSK5M7N"

headers = {
    
    "Authorization": f"{API_KEY}",
    "context": f"{context}",
    #"udid": f"{udid}",
    "lang": f"{lang}",
}



params = {
     "internalId": f"{params}"
 }


body = {
    "turnFormInternalId":"YSCKQPARBDOM2OFSRUC3NOTIIYXIRYW2G",
    "turnDeskInternalId":"UHFRPJ48EQAUGK4B3G30Q6DL7FUOD0S74",
    "appointmentDate": 6252024,
    "userName": "John",
    "userSurname": "Doe",
    "userDni": "",
    "userMail": "",
    "userTelephone": "",
    "userPassport": "",
    "userLicensePlate": "1111AAA",
}

if response_API.status_code == 200:
    response_API = requests.get("https://PROD-SERVER/mBase/api/v3.0/turnAppointments/", headers=headers)
    text_response = response_API.json()
    print(text_response)
else:
    print("No se puede conectar correctamente")
        