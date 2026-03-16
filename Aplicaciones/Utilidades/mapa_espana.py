import geopandas as gpd
import matplotlib.pyplot as plt
import pandas as pd

# --- Datos que me diste ---
data = {
    "Provincia": [
        "Cáceres","Cádiz","Castellón","Ciudad Real","Córdoba","A Coruña","Cuenca","Girona",
        "Granada","Guadalajara","Guipuzcoa","Huelva","Huesca","Jaén","León","Lleida",
        "La Rioja","Lugo","Madrid","Málaga","Murcia","Navarra","Ourense","Asturias",
        "Palencia","Palmas, Las","Pontevedra","Salamanca","Santa Cruz de Tenerife","Cantabria","Segovia","Sevilla",
        "Soria","Tarragona","Teruel","Toledo","Valencia","Valladolid","Vizcaya","Zamora",
        "Zaragoza","Ceuta","Melilla","Alava","Albacete","Alicante","Almería","Ávila",
        "Badajoz","Baleares","Barcelona","Burgos"
    ],
    "Número": [
        1,2,2,2,2,1,1,1,
        2,1,1,2,1,2,1,1,
        1,1,1,2,2,1,1,1,
        1,1,1,1,None,1,1,2,
        1,1,1,1,2,1,1,1,
        1,1,2,1,2,2,2,1,
        1,2,1,1
    ]
}

df = pd.DataFrame(data)

# --- Descargar shapefile ---
# 👉 Descárgalo desde:
# https://geodata.ucdavis.edu/gadm/gadm4.1/shp/gadm41_ESP_shp.zip
# Descomprime el ZIP en una carpeta y localiza el archivo: gadm41_ESP_2.shp

shapefile = r"C:\Users\jgmeras\OneDrive - GXO\Documents\01. Mahou\gadm41_ESP_shp\gadm41_ESP_2.shp"  # 👈 cambia esto con tu ruta
mapa = gpd.read_file(shapefile)

# Normalizar nombres para unir (quitamos tildes y ponemos en minúsculas)
df["Provincia_norm"] = (
    df["Provincia"]
    .str.normalize("NFKD")
    .str.encode("ascii", errors="ignore")
    .str.decode("utf-8")
    .str.lower()
)
mapa["NAME_2_norm"] = (
    mapa["NAME_2"]
    .str.normalize("NFKD")
    .str.encode("ascii", errors="ignore")
    .str.decode("utf-8")
    .str.lower()
)

# Unir shapefile con datos
mapa = mapa.merge(df, left_on="NAME_2_norm", right_on="Provincia_norm", how="left")

# Asignar colores
def get_color(num):
    if num == 1:
        return "blue"
    elif num == 2:
        return "red"
    else:
        return "white"

mapa["color"] = mapa["Número"].apply(get_color)

# --- Graficar ---
fig, ax = plt.subplots(1, 1, figsize=(10, 12))
mapa.plot(ax=ax, color=mapa["color"], edgecolor="black")

plt.title("Mapa de España por Provincias", fontsize=16)
plt.axis("off")
plt.show()

#Guardarlo en archivo PNG:
plt.savefig("mapa_espana_provincias.png", dpi=400, bbox_inches="tight")
