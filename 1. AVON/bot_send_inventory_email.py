from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib



from selenium.webdriver import Chrome
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys


import smtplib
from os.path import basename
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders



from email.message import EmailMessage
import os
import datetime
from datetime import datetime
import csv
import time
import re
import base64
import glob
from progress.bar import Bar


import urllib.request, urllib.error

import warnings
warnings.filterwarnings('ignore')

def actual_date():
    now = datetime.now()
    date_now = now.date()
   
    return date_now

def actual_hour():
    now = datetime.now()
    hour_now = now.time()

    return hour_now

def select_file():
    
    list_of_files = glob.glob("C:\\Users\\jgmeras\\Downloads\\*.xlsx") # * means all if need specific format then *.csv
    #list_of_files = glob.glob("C:\\Users\\lublasco\\Downloads\\*.xlsx")
    latest_file = max(list_of_files, key=os.path.getctime)
         
    return latest_file        
    

def change_path():
    path_source = select_file()
    print(path_source)
    name_head, name_tail = os.path.split(select_file())
    path_destination = "C:\\Users\\jgmeras\\Documents\\Python Scripts\\" + name_tail
    #path_destination = "C:\\Users\\lublasco\\Documents\\Python Scripts\\" + name_tail
    print(path_destination)

    os.replace(path_source, path_destination)

def select_file2():
    pattern = r"\\([\d]{8})"
    pattern_date = r"^([\d]*)-([\d]*)-([\d]*)"
    #pattern_third = r"(\[\]\')"

    date_now = str(actual_date())
    control_date = re.sub(pattern_date, r"\1\2\3", date_now)
    
    dir = os.getcwd()
    
    for name in os.listdir(dir):
        fullname = os.path.join(dir, name)
        
        if not os.path.isdir(fullname):
            
            sub_result = re.search(pattern, fullname)
            
            #result = re.sub(pattern_third,  r"", str(sub_result))
            if any(x in sub_result[0] for x in control_date):
                return name
            else:
                print("REVISAR")

fecha = actual_date()
hora = actual_hour()

message = ("""

Enviado inventario a dia {} {}




<p class=MsoNormal><span style='font-size:10.0pt;font-family:"Arial",sans-serif;
color:black;mso-fareast-language:ES'><o:p>&nbsp;</o:p></span></p>

<p class=MsoNormal><span style='font-size:10.0pt;font-family:"Arial",sans-serif;
color:black;mso-fareast-language:ES'>Thank you<o:p></o:p></span></p>

<p class=MsoNormal><b><span style='font-size:10.0pt;font-family:"Arial Black",sans-serif;
color:black;mso-fareast-language:ES'><o:p>&nbsp;</o:p></span></b></p>

<p class=MsoNormal><b><span style='font-size:10.0pt;font-family:"Arial Black",sans-serif;
color:black;mso-fareast-language:ES'>Javier Garcia-Meras<o:p></o:p></span></b></p>

<p class=MsoNormal><span lang=PT style='font-size:8.5pt;font-family:"Arial",sans-serif;
color:#333333;mso-ansi-language:PT;mso-fareast-language:ES'>Inventory Team/Data Analyst</span><span
lang=PT style='color:#1F497D;mso-ansi-language:PT;mso-fareast-language:ES'><o:p></o:p></span></p>

<p class=MsoNormal style='background:white'><span lang=PT style='font-size:
5.0pt;font-family:"Arial",sans-serif;color:#333333;mso-ansi-language:PT;
mso-fareast-language:ES'>&nbsp;<o:p></o:p></span></p>

<p class=MsoNormal style='line-height:12.0pt;background:white'><b><span
lang=PT style='font-size:12.0pt;font-family:"Arial Black",sans-serif;
color:#FF3A00;letter-spacing:-.7pt;mso-ansi-language:PT;mso-fareast-language:
ES'>GXO<o:p></o:p></span></b></p>

<p class=MsoNormal style='line-height:10.0pt;background:white'><span lang=PT
style='font-size:8.0pt;font-family:"Arial",sans-serif;color:#333333;mso-ansi-language:
PT;mso-fareast-language:ES'>Avenida de la Veguilla, 9, nave D <o:p></o:p></span></p>

<p class=MsoNormal style='line-height:10.0pt;background:white'><span
style='font-size:8.0pt;font-family:"Arial",sans-serif;color:#333333;mso-fareast-language:
ES'>Cabanillas del Campo 19171, Guadalajara ES<o:p></o:p></span></p>

<p class=MsoNormal><span style='mso-fareast-language:ES'><o:p>&nbsp;</o:p></span></p>

<p class=MsoNormal><o:p>&nbsp;</o:p></p>

<p class=MsoNormal><o:p>&nbsp;</o:p></p>

""").format(fecha, hora)

# ****** URL DE PRODUCCION ******
url = "https://bax11s.am.gxo.com/avon/login/"

headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36", "Accept-Encoding":"gzip, deflate", "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8", "DNT":"1","Connection":"close", "Upgrade-Insecure-Requests":"1"}

driver_options = Options()
driver_options.add_argument(headers)
driver_options.add_argument('--no-sandbox')

driver = webdriver.Chrome()
driver.maximize_window()
driver.get(url)
#driver.execute_script("window.scrollTo(500, 1080);")

time.sleep(5)

#loguear

decoded_user = base64.b64decode("anBhbGFjaW9z")
decoded_pw = base64.b64decode("U2VjdXJpdHlAMTIzNA==")

user = decoded_user.decode("utf-8")
passw = decoded_pw.decode("utf-8")

user_login = driver.find_element("xpath", "//*[@id='username']").send_keys(user)
user_passw = driver.find_element("xpath", "//*[@id='password']").send_keys(passw)
user_passw = driver.find_element("xpath", "//*[@id='password']").send_keys(Keys.RETURN)

time.sleep(10)

#buscar la opcion correcta de Adhoc

main_menu1 = driver.find_element("xpath", "/html/body/div[4]/div/div[2]/div[2]/div[2]/table/tbody/tr[1]/td[1]").text
main_menu2 = driver.find_element("xpath", "/html/body/div[4]/div/div[2]/div[2]/div[2]/table/tbody/tr[2]/td[1]").text
main_menu3 = driver.find_element("xpath", "/html/body/div[4]/div/div[2]/div[2]/div[2]/table/tbody/tr[3]/td[1]").text
main_menu4 = driver.find_element("xpath", "/html/body/div[4]/div/div[2]/div[2]/div[2]/table/tbody/tr[4]/td[1]").text



if main_menu1 == "Adhoc Insights":
    main_menu1 = driver.find_element("xpath", "/html/body/div[4]/div/div[2]/div[2]/div[2]/table/tbody/tr[1]/td[1]/a").click()
if main_menu2 == "Adhoc Insights":
    main_menu2 = driver.find_element("xpath", "/html/body/div[4]/div/div[2]/div[2]/div[2]/table/tbody/tr[2]/td[1]/a").click()
if main_menu3 == "Adhoc Insights":
    main_menu3 = driver.find_element("xpath", "/html/body/div[4]/div/div[2]/div[2]/div[2]/table/tbody/tr[3]/td[1]/a").click()
if main_menu4== "Adhoc Insights":
    main_menu4 = driver.find_element("xpath", "/html/body/div[4]/div/div[2]/div[2]/div[2]/table/tbody/tr[4]/td[1]/a").click()  
else: 
    print("transicion")

time.sleep(15)

# seleccionamos Warehouse Inventory by SKU

i_menu_sku = driver.find_element("xpath", "/html/body/div[2]/div/div/div[2]/div/div/div/div/div/div/div/div/div/div/div/div/div/div/div/div[2]/div[1]/div/div/div/div/div/div[1]/div/div/p[1]/button[4]").click()
time.sleep(15)

#vamos al menu para descargar el fichero

#boton pagina inventario

i_menu_excel = driver.find_element("xpath", "html/body/div[2]/div/div/div[2]/div/div/div/div/div/div/div/div/div/div/div/div/div/div/div/div/div/div/div/div/div/div/div/div/div/div/div/div/div/div/div/div/div/div[2]/div[1]/div/div/div/div[1]/div/article/div[1]/div/div/div[2]/button/div/span[2]").click()

#seleccionar download

download_excel = driver.find_element("xpath", "/html/body/div[2]/div/div/div[2]/div/div/div/div/div/div/div/div/div/div/div/div/div/div/div/div/div/div/div/div/div/div/div/div/div/div/div/div/div/div/div/div/div/div[2]/div[1]/div/div/div/div[1]/div/article/div[1]/div/div/div[2]/ul/li[7]/a").click()

time.sleep(60)  

#Cambiar el archivo a la carpeta de trabajo

change_path()
time.sleep(2)

#Configurar el Mensaje

msg = MIMEMultipart()

files =  select_file2()

user = 'javier.garcia-meras-palacios@gxo.com'
#destinataries = ['javier.garcia-meras-palacios@gxo.com', 'yohan-antonio.rodriguez-silva@gxo.com', 'luis.blasco@gxo.com', 'veruska.iglesiasgonzalez@gxo.com', 'aisha.bennai@gxo.com']

msg['From'] = user
msg['To'] = user
msg['Subject'] = ("[AVON] Inventario Diario {} {}").format(fecha, hora)
msg.attach(MIMEText(message, 'html','utf8'))

part = MIMEBase('application', "octet-stream")
with open(files, 'rb') as file:
    part.set_payload(file.read())
encoders.encode_base64(part)
part.add_header('Content-Disposition',
                'attachment; filename={}'.format(files))
msg.attach(part)

#Configurar el servidor y enviar el mensaje

server = smtplib.SMTP('10.19.30.20:25' )
server.set_debuglevel(1)


server.ehlo()
server.starttls()
server.ehlo()



try:
    server.sendmail(
        msg['From'],
        msg['To'],
        #destinataries,
        msg.as_string())
 
    server.quit()
 
    print ("successfully sent email to %s:" % (msg['To']))
except:
    print("unable to connect")

driver.close()
print("close connect")

#eliminar el archivo

os.remove(select_file2())
