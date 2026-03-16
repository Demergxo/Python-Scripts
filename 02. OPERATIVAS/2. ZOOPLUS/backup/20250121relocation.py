# Author: Javier García-Merás Palacios
# version: 0.1
# Description: Archivo para gestión y generación de reportes para el equipo de GDS


from base64 import b64decode
from tkinter import Image, Toplevel
from PIL import Image, ImageTk

import tempfile
import tkinter as tk
import os
from tkinter import ttk
from tkinterdnd2 import TkinterDnD, DND_FILES

import pandas as pd
from trio import Condition



raw_image = "iVBORw0KGgoAAAANSUhEUgAAAHwAAAAuCAMAAADdho1wAAAAV1BMVEVHcEz/OgD/OgD/OgD/OgD/OgD/OgD/OgD/OgD/OgD/OgD/OgD/OgD/OgD/OgD/OgD/OgD/OgD/OgD/OgD/OgD/OgD/OgD/OgD/OgD/OgD/OgD/OgD/OgD/maxbAAAAHHRSTlMAOZ4DJi3nBvftGwy7zNVo3RNcRk20w4eoe5JvWvIB4QAAA/5JREFUWMPNWNuypCoMbS94Q1QUUdT//85x79Y2IRG7ps6pmlQ/AWZ1FrmR1+tfk0RqrWX+H2nL5dfKdNQuo1VK2TF2pkqunUpckiJleQq2JNa2vrXVsRuqB5OjSZXbJUU3959Phq78SNbDr/rs2rEV0lYAZU08yHvsKIbIhzTuUJfHYFUBM9IGIPQhbUVtbvjXEwP9I6OkINt0GQj/VHwq1y7jdBVxyppteeitWM8jPSCxjM5VA1abU7UYb7RtzUCxTXd3ev5cFCL+5KNSDOlRs91K2RPs7O5sJ25ut32vTQzpUbdt36Pfnz4xKPHdL8VRSUlPmy0oJWK+stsz6YT4ZU8CcqSky3F7kAZ4XbL45pZZVhDSf06mgKLCvF4rQ7rzte3iLcVXxA0oxgrlBpGKqI87GLaHtECP1aKj5ogMh7YzUWRcjfB//vfB5YwcrNVvI/fbcBNJSRIedjHj6YhGaw4N0lgudyCf2SziOaExCY2FdJ5MIsNjkAgr+LeLgfmrSjyWnrYI+hC88VmjFArR42OtuQsCXhDxhHRpeaf2Q7B5czJA7pIvqr1gksLHfQW4w9X/dCW8r1zCDsoaCNweuC4p4BUw3f2uAI+10LmHtb1kNYATkkVARE7kWqEs3m5ec3VyjwGc7ev8fg/mDGBKyzirp1Aq9rhvHQJ/rcVNtsxHGk3wX1/fKek5O8hnfo7E4FrBvQUk/4vHgnEg4I6N9sDNLbEeuEEJuRFfgic+OEu7rrcQeKW80pdztJtn2lmHc1sInFbB677mQJijQHwrBP455lyZI+CGJNguZUJtTh5DDVqZvS8vd/X4lowD90lHwQZsy9JQklmJHe64uVNiBpyQjoiH6XUKhPkRiFXHd4v4Si5wUwaqWgILSxYFCoumTf+on8BRq/zQRNnqthwunP/E+gEckF442rPDUN6/AtdeQSM/JUyiBqeOLicF4X6CQ9LnvKevFUTk1hxNmd9GXZmhR6FTxqaS+f6qFqsioQZJ36+UtNIkORZq6gfSQILanXu9SdHZcaybksZ5At8nzu/oDH3DnL2ztwLjQDRPbf4BDkm32m8sjtaI5mZfsCOa8itwSPrR7iGkg3jRhXV1OAST/gn9p7tDpB9AKBWfxA9ZSFVGCn0fPF/8NuBDyTUQEzOwGAK2d0yTMajA+T73npNXHUtQqj/5uB017KHM9aTVckN9tqTE0+HjFQ0sziJe8UOWctJ3s6iZ+aBbBL3cDNYAFKmfSRGnrZwDvXkeTdYbhbXp8WLT4/5uPgX3CaIBWw5qQ6MwNUUPs0Ap+mmurVJ2XtYBDAFlCsR7vFZgC84NPyNFOy5tpL94De2/XO6SvP5CEm6Y+rfK/lf5A5RpN2/mmB9oAAAAAElFTkSuQmCC"
user = os.environ['USERNAME']
ruta_archivo_sbl =""
ruta_archivo_rel =""

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

def pantalla_trabajo():
    global ruta_archivo_rel
    global ruta_archivo_sbl
    def procesar_archivos(ruta_archivo_sbl, ruta_archivo_rel):
        #seleccionar y filtrar Stock by Location
        ruta_sbl = ruta_archivo_sbl
        df_sbl = pd.read_excel(ruta_sbl, sheet_name="Stockporubicación", header=5, usecols="B:X")
        
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
        df_resul = pd.DataFrame(columns=["Artículo", "Qty", "Soporte", "Ubicación"])
        
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
                
                cantidad_disponible = inv_row["Unds. Totales"]
                soporte = str(inv_row["NÂ° Support"])
                ubicacion = inv_row["Location"]
                
                if cantidad_acumulada + cantidad_disponible <= cantidad_necesaria:
                    #si el la cantidad disponible es completamente usada
                    df_resul = pd.concat([df_resul, pd.DataFrame({
                        "Artículo": [articulo],
                        "Qty" : [cantidad_disponible],
                        "Soporte": [soporte],
                        "Ubicación": [ubicacion]
                    })], ignore_index=True)
                    cantidad_acumulada += cantidad_disponible
                else:
                    #si solo se necesita parte
                    df_resul = pd.concat([df_resul, pd.DataFrame({
                        "Artículo": [articulo],
                        "Qty" : [cantidad_necesaria - cantidad_acumulada],
                        "Soporte": [soporte],
                        "Ubicación": [ubicacion] 
                    })], ignore_index=True)
                    cantidad_acumulada = cantidad_necesaria
        #print(df_rel_filtrado)
                
        #print(df_ordenado)
        df_resul.to_excel("resultado.xlsx", index=True)
        #print(df_resul)
        
    procesar_archivos(ruta_archivo_sbl=ruta_archivo_sbl, ruta_archivo_rel=ruta_archivo_rel)
        
        

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