# Author: Javier García-Merás Palacios
# version: 0.1
# Description: Archivo para gestión y generación de reportes para el equipo de GDS
# import os
# import sys

# # Obtener la ruta del ejecutable o del script
# if getattr(sys, 'frozen', False):
#     # Si está congelado con cx_Freeze
#     base_path = sys._MEIPASS #type: ignore
# else:
#     base_path = os.path.dirname(os.path.abspath(__file__))

# # Asegurar que la ruta de tkdnd está bien definida
# tkdnd_path = os.path.join(base_path, "tcl", "tkdnd")

# # Establecer TCL_LIBRARY para que encuentre los paquetes Tcl/Tk
# os.environ["TCL_LIBRARY"] = os.path.join(base_path, "share", "tcl8.6")
# os.environ["TK_LIBRARY"] = os.path.join(base_path, "share", "tk8.6")

# # Agregar manualmente tkdnd a la ruta de Tcl
# os.environ["TKDND_LIBRARY"] = tkdnd_path

# import tkinterdnd2 


import logging
logging.basicConfig(filename="app.log", level=logging.DEBUG)


from base64 import b64decode
from tkinter import Image, Toplevel
from PIL import Image, ImageTk

from io import BytesIO
import tempfile
import tkinter as tk
import os
from tkinter import ttk
from tkinterdnd2 import *

import sys
import pandas as pd
import datetime

date = datetime.datetime.now().strftime("%Y%m%d")
raw_image = "iVBORw0KGgoAAAANSUhEUgAAAHwAAAAuCAMAAADdho1wAAAAV1BMVEVHcEz/OgD/OgD/OgD/OgD/OgD/OgD/OgD/OgD/OgD/OgD/OgD/OgD/OgD/OgD/OgD/OgD/OgD/OgD/OgD/OgD/OgD/OgD/OgD/OgD/OgD/OgD/OgD/OgD/maxbAAAAHHRSTlMAOZ4DJi3nBvftGwy7zNVo3RNcRk20w4eoe5JvWvIB4QAAA/5JREFUWMPNWNuypCoMbS94Q1QUUdT//85x79Y2IRG7ps6pmlQ/AWZ1FrmR1+tfk0RqrWX+H2nL5dfKdNQuo1VK2TF2pkqunUpckiJleQq2JNa2vrXVsRuqB5OjSZXbJUU3959Phq78SNbDr/rs2rEV0lYAZU08yHvsKIbIhzTuUJfHYFUBM9IGIPQhbUVtbvjXEwP9I6OkINt0GQj/VHwq1y7jdBVxyppteeitWM8jPSCxjM5VA1abU7UYb7RtzUCxTXd3ev5cFCL+5KNSDOlRs91K2RPs7O5sJ25ut32vTQzpUbdt36Pfnz4xKPHdL8VRSUlPmy0oJWK+stsz6YT4ZU8CcqSky3F7kAZ4XbL45pZZVhDSf06mgKLCvF4rQ7rzte3iLcVXxA0oxgrlBpGKqI87GLaHtECP1aKj5ogMh7YzUWRcjfB//vfB5YwcrNVvI/fbcBNJSRIedjHj6YhGaw4N0lgudyCf2SziOaExCY2FdJ5MIsNjkAgr+LeLgfmrSjyWnrYI+hC88VmjFArR42OtuQsCXhDxhHRpeaf2Q7B5czJA7pIvqr1gksLHfQW4w9X/dCW8r1zCDsoaCNweuC4p4BUw3f2uAI+10LmHtb1kNYATkkVARE7kWqEs3m5ec3VyjwGc7ev8fg/mDGBKyzirp1Aq9rhvHQJ/rcVNtsxHGk3wX1/fKek5O8hnfo7E4FrBvQUk/4vHgnEg4I6N9sDNLbEeuEEJuRFfgic+OEu7rrcQeKW80pdztJtn2lmHc1sInFbB677mQJijQHwrBP455lyZI+CGJNguZUJtTh5DDVqZvS8vd/X4lowD90lHwQZsy9JQklmJHe64uVNiBpyQjoiH6XUKhPkRiFXHd4v4Si5wUwaqWgILSxYFCoumTf+on8BRq/zQRNnqthwunP/E+gEckF442rPDUN6/AtdeQSM/JUyiBqeOLicF4X6CQ9LnvKevFUTk1hxNmd9GXZmhR6FTxqaS+f6qFqsioQZJ36+UtNIkORZq6gfSQILanXu9SdHZcaybksZ5At8nzu/oDH3DnL2ztwLjQDRPbf4BDkm32m8sjtaI5mZfsCOa8itwSPrR7iGkg3jRhXV1OAST/gn9p7tDpB9AKBWfxA9ZSFVGCn0fPF/8NuBDyTUQEzOwGAK2d0yTMajA+T73npNXHUtQqj/5uB017KHM9aTVckN9tqTE0+HjFQ0sziJe8UOWctJ3s6iZ+aBbBL3cDNYAFKmfSRGnrZwDvXkeTdYbhbXp8WLT4/5uPgX3CaIBWw5qQ6MwNUUPs0Ap+mmurVJ2XtYBDAFlCsR7vFZgC84NPyNFOy5tpL94De2/XO6SvP5CEm6Y+rfK/lf5A5RpN2/mmB9oAAAAAElFTkSuQmCC"
raw_search_image = "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"
logo_zooplus ="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"
user = os.environ['USERNAME']
ruta_archivo_sbl =""
ruta_archivo_rel =""




# Decodificar la imagen y asignarla a un Label en la ventana secundaria
def mostrar_imagen_base64(base64_string, parent, x, y):
    raw_image_data = b64decode(base64_string)
    image = Image.open(BytesIO(raw_image_data))
    photo = ImageTk.PhotoImage(image, master=parent)  # Especificar el master para TkinterDnD

    # Crear un Label con la imagen
    label = tk.Label(parent, image=photo) #type:ignore
    label.image = photo  # type: ignore Mantener la referencia para evitar la recolección de basura
    label.place(x=x, y=y)

def cargar_ficheros():
    
    def archivo_arrastrado(event):
        global ruta_archivo_sbl
        #Obtener la ruta del archivo arrastrado
        ruta_archivo_sbl = event.data.strip("{}")
        # Actualizar el contenido de Entry con la ruta
        entrada_ruta.delete(0, tk.END)
        entrada_ruta.insert(0, ruta_archivo_sbl)
        
    def archivo_arrastrado2(event):
        global ruta_archivo_rel
        #Obtener la ruta del archivo arrastrado
        ruta_archivo_rel = event.data.strip("{}")
        # Actualizar el contenido de Entry con la ruta
        entrada_ruta2.delete(0, tk.END)
        entrada_ruta2.insert(0, ruta_archivo_rel)
    
    def cerrar_app2():
        app2.destroy()
        app.deiconify()
    
    # Determinar la ubicación de los archivos tkdnd
    if hasattr(sys, "_MEIPASS"):  # Para ejecutables generados
        base_path = sys._MEIPASS #type: ignore
    else:  # Para entornos de desarrollo
        base_path = os.path.dirname(os.path.abspath(__file__))

    tkdnd_path = os.path.join(base_path, "tkdnd")
    os.environ["TKDND_LIBRARY_PATH"] = tkdnd_path
    
    
    app.withdraw()
    app2 = TkinterDnD.Tk()
    app2.geometry("650x300")
    app2.title("Cargar Ficheros")
    
    app2.grab_set()
    
    label_stockbylocation = tk.Label(
        app2,
        text="Stock by Location",
        foreground="black",
        font=("Helvetica", 12, "bold")
    )
    label_stockbylocation.place(x=50, y=30)
    
    entrada_ruta = tk.Entry(
        app2,
        font=("Arial", 12),
        width=40,
        state="normal"
    )
    entrada_ruta.place(x=50, y=60)
    
    zona_arrastre = tk.Label(
        app2,
        text="Stock by Location aquí",
        bg="lightblue",
        width=25,
        height=2,
        relief="groove"
        )
    zona_arrastre.place(x=450, y=47)
    
    zona_arrastre.drop_target_register(DND_FILES) #type: ignore
    zona_arrastre.dnd_bind('<<Drop>>', archivo_arrastrado) #type: ignore
    
    
    label_relocation_cliente = tk.Label(
        app2,
        text="Archivo Relocation",
        foreground="black",
        font=("Helvetica", 12, "bold")
    )
    label_relocation_cliente.place(x=50, y=90)
    
    entrada_ruta2 = tk.Entry(
        app2,
        font=("Arial", 12),
        width=40,
        state="normal"
    )
    entrada_ruta2.place(x=50, y=120)
    
    zona_arrastre2 = tk.Label(
        app2,
        text="Archivo Relocation aquí",
        bg="lightblue",
        width=25,
        height=2,
        relief="groove"
        )
    zona_arrastre2.place(x=450, y=111)
    
    zona_arrastre2.drop_target_register(DND_FILES) #type: ignore
    zona_arrastre2.dnd_bind('<<Drop>>', archivo_arrastrado2) #type: ignore
 
    button_salir_app2 = tk.Button(
        app2,
        text="Salir",
        command=cerrar_app2,
        width=12,
        foreground="red"
    )
    button_salir_app2.place(x=270, y=250)

    mostrar_imagen_base64(raw_search_image, app2, 495, 175)
    mostrar_imagen_base64(logo_zooplus, app2, 25, 165)
    
def pantalla_trabajo():
    global ruta_archivo_rel
    global ruta_archivo_sbl
    def procesar_archivos(ruta_archivo_sbl, ruta_archivo_rel):
        #seleccionar y filtrar Stock by Location
        ruta_sbl = ruta_archivo_sbl
        df_sbl = pd.read_excel(ruta_sbl, sheet_name="Stockporubicación", header=4, usecols="B:X")
        
        #seleccionar solo lo que empieza por B, H y R y solo por condición A
        df_filtrado = df_sbl[df_sbl["Pasillo"].str.startswith(('B', 'H', 'R'), na=False) & (df_sbl["Condition"] == "A")]
        
        #Ordenar por altura de mayor a menor y por fecha de más antigua a más reciente
        df_ordenado = df_filtrado.sort_values(by=["Altura", "Exp. date"], ascending=[False, True])
        df_ordenado["Location"] = df_ordenado["Pasillo"].astype(str) + df_ordenado["Cara"].astype(str)  + df_ordenado["Columna"].apply(lambda x: f"{int(x):03}").astype(str)  + df_ordenado["Altura"].apply(lambda x: f"{int(x):02}").astype(str)  + df_ordenado["PosiciÃ³n"].astype(str) 
        
        #seleccionar y filtrar archivo relocation
        ruta_rel = ruta_archivo_rel
        df_rel = pd.read_excel(ruta_rel, header=6, usecols="A:F")
        #quedarnos solo con las columnas que nos interesan
        columnas_interes = ["Article Id", "Quantity"]
        
        df_rel_filtrado = df_rel[columnas_interes]
        
        #crear dataframe resultado
        df_resul = pd.DataFrame(columns=["Artículo", "Descripción", "Qty", "Soporte", "Ubicación"])
        
        #iterar en df_rel para comparar
        for _, row in df_rel_filtrado.iterrows():
            articulo = row["Article Id"]
            cantidad_necesaria = row["Quantity"]
            
            #filtrar para obtener las filas del artículo actual
            inventario = df_ordenado[df_ordenado["ArtÃ­culo"] == articulo]
            
            cantidad_acumulada = 0
            
            for _, inv_row in inventario.iterrows():
                if cantidad_acumulada >= cantidad_necesaria:
                    break
                
                descripcion = str(inv_row["DesignaciÃ³n"])
                cantidad_disponible = inv_row["Unds. Totales"]
                soporte = str(inv_row["NÂ° Support"])
                ubicacion = inv_row["Location"]
                
                if cantidad_acumulada + cantidad_disponible <= cantidad_necesaria:
                    #si el la cantidad disponible es completamente usada
                    df_resul = pd.concat([df_resul, pd.DataFrame({
                        "Artículo": [articulo],
                        "Descripción": [descripcion],
                        "Qty" : [cantidad_disponible],
                        "Soporte": [soporte],
                        "Ubicación": [ubicacion]
                    })], ignore_index=True)
                    cantidad_acumulada += cantidad_disponible
                else:
                    #si solo se necesita parte
                    df_resul = pd.concat([df_resul, pd.DataFrame({
                        "Artículo": [articulo],
                        "Descripción": [descripcion],
                        "Qty" : [cantidad_necesaria - cantidad_acumulada],
                        #"Soporte": [soporte],
                        "Ubicación": [ubicacion] 
                    })], ignore_index=True)
                    cantidad_acumulada = cantidad_necesaria
        #print(df_rel_filtrado)
                
        #print(df_ordenado)
        df_resul.to_excel(f"{date}resultado.xlsx", index=False)
        #print(df_resul)
        
    procesar_archivos(ruta_archivo_sbl=ruta_archivo_sbl, ruta_archivo_rel=ruta_archivo_rel)
        
        
#ventanana principal
app = tk.Tk()
icon_main ="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"

icon_path = os.path.join(tempfile.gettempdir(), "app_icon.ico")
with open(icon_path, "wb") as icon_file:
    icon_file.write(b64decode(icon_main))
    
app.geometry("450x300")
app.title("Relocation")

app.iconbitmap(icon_path)

label = ttk.Label(
    app,
    text="Relocations",
    foreground="black",
    font=("Helvetica", 20, "bold")
)
label.place(x=60, y=40)

button_cargar_fichers = tk.Button(
    app,
    text="Cargar Ficheros",
    command=cargar_ficheros,
    width=15
)
button_cargar_fichers.place(x=50, y=100)

button_pantalla_trabajo = tk.Button(
    app,
    text="Ventana de Tabajo",
    command=pantalla_trabajo,
    width=15
)
button_pantalla_trabajo.place(x=250, y=100)


button_salir = tk.Button(
    app,
    text="Salir",
    command=app.destroy,
    width=12,
    foreground="red"
)
button_salir.place(x=270, y=250)

raw_image_data = b64decode(raw_image)
with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as temp_image_file:
    temp_image_file.write(raw_image_data)
    temp_image_path = temp_image_file.name

image = Image.open(temp_image_path)
photo = ImageTk.PhotoImage(image)

label2 = tk.Label(app, image=photo, text="")#type: ignore
label2.place(x=275, y=185)

app.mainloop()