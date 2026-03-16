from selenium import webdriver
from selenium.webdriver.common.by import By
import csv
import time
 
driver = webdriver.Chrome()
driver.get("https://www.vinted.es/catalog?search_text=funko+pop")
time.sleep(5)
 
# Acepta cookies si aparecen
try:
    accept_btn = driver.find_element(By.XPATH, '//button[contains(text(), "Aceptar")]')
    accept_btn.click()
except:
    pass
 
# Desplaza para cargar más productos
for _ in range(5):
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(2)
 
# Extrae productos
items = driver.find_elements(By.CLASS_NAME, 'feed-grid__item')
datos = []
 
for item in items:
    print("1")
    try:
        print("2")
        titulo = item.find_element(By.CLASS_NAME, 'title__text').text
        print(titulo)
        precio = item.find_element(By.CLASS_NAME, 'price__amount').text
        print(precio)
        enlace = item.find_element(By.TAG_NAME, 'a').get_attribute('href')
        print
        datos.append([titulo, precio, enlace])
    except:
        print("3")
        continue
 
driver.quit()
 
# Guarda en CSV
with open('funkos.csv', mode='w', newline='', encoding='utf-8') as archivo:
    writer = csv.writer(archivo)
    writer.writerow(['Nombre del producto', 'Precio', 'Enlace'])
    writer.writerows(datos)