from datetime import datetime
import time

from selenium.webdriver import Chrome
from selenium import webdriver
#from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait as wait #type: ignore

import base64
import re
import pandas as pd

def actual_date():
    #no es necesario modificar el formato, coincide con el de Transporeon (yyyy-mm-dd)
    now = datetime.now()
    date_now = now.date()
    #print(date_now)
    return date_now


    
def trp_to_mturn(list_element):
    date = actual_date()
    name_file = "TRP_TO_MTURN" + str(date) + ".csv"
    
    # Crear un DataFrame de pandas
    df = pd.DataFrame(list_element, columns=["Hora", "Proveedor", "Tractora", "PO"])
    
    # Guardar el DataFrame como un archivo CSV
    df.to_csv(name_file, index=False)
            
def clean_string(string):
    pattern = r":\s*(.*)$"
    result = re.search(pattern, string)
    
    if result:
        return_string = result.group(1)
        return return_string.upper()
    
    
# ****** URL DE PRODUCCION ******
url = "https://login.transporeon.com/login/"
 
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36", "Accept-Encoding":"gzip, deflate", "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8", "DNT":"1","Connection":"close", "Upgrade-Insecure-Requests":"1"}

driver_options = Options()
driver_options.add_argument(headers)
driver_options.add_argument('--no-sandbox')

driver = webdriver.Chrome()
driver.maximize_window()
driver.get(url)
#driver.execute_script("window.scrollTo(500, 1080);")

time.sleep(5)

#loguear

decoded_user = base64.b64decode("cmFmYWVsLmFycmVkb25kb0B4cG8uY29t")
decoded_pw = base64.b64decode("QW1hem9uMjk3Mw==")

user = decoded_user.decode("utf-8")
passw = decoded_pw.decode("utf-8")

user_login = driver.find_element("xpath", "/html/body/div[2]/table/tbody/tr[1]/td/div/div[2]/table/tbody/tr/td[2]/form/div/div[2]/div/div/div/div[2]/div/div/div[2]/div/input").send_keys(user)
user_passw = driver.find_element("xpath", "/html/body/div[2]/table/tbody/tr[1]/td/div/div[2]/table/tbody/tr/td[2]/form/div/div[2]/div/div/div/div[3]/div/div/div[2]/div/input").send_keys(passw)
driver.find_element("xpath", "/html/body/div[2]/table/tbody/tr[1]/td/div/div[2]/table/tbody/tr/td[2]/form/div/div[2]/div/div/div/div[7]/div/div/div/div").click()

time.sleep(7)

#acceder al menú correspondiente

try:
    driver.find_element("xpath", "/html/body/div[4]/div[2]/div[2]/div/div[2]/div[1]/div[2]").click()
    time.sleep(7)
except:
    pass

#cambiamos de iframe
wait(driver, 5).until(EC.frame_to_be_available_and_switch_to_it("iFrameRetailTSM"))
driver.find_element("xpath", "/html/body/tsm3-root/app-sidebar-layout/div/aside/tpg-sidebar-navigation/div/div[1]/div[2]/tpg-navigation-item/a/div[1]").click()
driver.find_element("xpath", "/html/body/tsm3-root/app-sidebar-layout/div/aside/tpg-sidebar-navigation/div/div[1]/div[2]/div/div[2]/tpg-navigation-item/a/div/div/div[2]").click()

#definir cuanto tiempo queremos

#volvemos a cambiar de Iframe
wait(driver, 3).until(EC.frame_to_be_available_and_switch_to_it("mclegacy"))

#Primera posicion de la parrilla

time.sleep(3)

count = 2

separator = ","
list_element = []

for  i in range(1, 15):

    try:
        
        hour = driver.find_element("xpath", "/html/body/div[1]/div/div[2]/div[2]/div/div/div/div[1]/div/div/div/div/div/table/tbody/tr["+str(count)+"]/td[1]/span").text
        po = driver.find_element("xpath","/html/body/div[1]/div/div[2]/div[2]/div/div/div/div[1]/div/div/div/div/div/table/tbody/tr["+str(count)+"]/td[3]/div/div[2]/div/div[2]/div[2]").text
        plate = driver.find_element("xpath","/html/body/div[1]/div/div[2]/div[2]/div/div/div/div[1]/div/div/div/div/div/table/tbody/tr["+str(count)+"]/td[3]/div/div[2]/div/div[2]/div[3]").text
        provider = driver.find_element("xpath","/html/body/div[1]/div/div[2]/div[2]/div/div/div/div[1]/div/div/div/div/div/table/tbody/tr["+str(count)+"]/td[3]/div/div[2]/div/div[2]/div[7]").text

        #limpiamos la cadenas
        po = clean_string(po)
        plate = clean_string(plate)
        provider = clean_string(provider)
        
        
        if not isinstance(po, str):
            break
            
        else:
            #result = str(hour) + separator + str(plate)+ str(po)
            print("PO: {}".format(po))
            print(f"provider: {provider}")
            list_element.append([hour, provider, plate, po])
        
        
        #print(list_element)
        count = count + 1
            
    except:
        count = count + 1
        pass
trp_to_mturn(list_element)
for i in list_element:
    print(i)
    
time.sleep(3)
driver.close()
print("Close conection")
    

