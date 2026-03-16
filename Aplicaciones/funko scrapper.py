from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
import time
import csv
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

date = time.strftime("%Y%m%d")

# Configura opciones del navegador para evitar detección
options = Options()
options.add_argument("--start-maximized")
driver = webdriver.Chrome(options=options)

# Abrir Vinted
driver.get("https://www.vinted.es/")
time.sleep(5)

# Acepta cookies si aparecen
try:
    accept_btn = driver.find_element(By.XPATH, '//button[contains(text(), "Aceptar")]')
    accept_btn.click()
    time.sleep(2)
except:
    pass

# Buscar "funko pop"
search_box = driver.find_element(By.CLASS_NAME, 'web_ui__InputBar__value')
search_box.clear()
search_box.send_keys("funko pop")
time.sleep(1)
search_box.send_keys(Keys.RETURN)
time.sleep(5)

# Scroll para cargar más resultados
SCROLL_PAUSES = 10
for _ in range(SCROLL_PAUSES):
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(3)

# Extraer los elementos
items = driver.find_elements(By.CLASS_NAME, 'feed-grid__item')

results = []

for item in items:
    try:
        lines = item.text.strip().split("\n")
        link = item.find_element(By.TAG_NAME, "a").get_attribute("href")

        if len(lines) >= 4:
            title = lines[0]
            description = lines[1]
            price = lines[3]
            results.append([title, description, price, link])
    except Exception as e:
        print("Error en item:", e)
        continue

driver.quit()

# Guardar en CSV
with open(f'{date}-funkos.csv', mode='w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(['Titulo', 'Descripcion', 'Precio', 'Enlace'])
    writer.writerows(results)

print("✅ ¡Archivo funkos.csv creado con éxito!")
