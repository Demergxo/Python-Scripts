#Author: Javier García-Merás Palacios
#version : 2.7
#Description: Aplicación de centralización de archivos, creando botones que muestra puntos especificos de un share-point para automatizar y mejorar tiempos de acceso en trabajos diarios

from tkinter import Image, Listbox, filedialog, messagebox, ttk, StringVar
import os
from functools import partial
from base64 import b64decode
import tempfile

from PIL import Image, ImageTk
import tkinter as tk

from textwrap import wrap

def ajustar_texto(texto, ancho_maximo):
    # Dividir el texto en líneas con el ancho máximo
    return "\n".join(wrap(texto, width=ancho_maximo))

raw_image = "iVBORw0KGgoAAAANSUhEUgAAAHwAAAAuCAMAAADdho1wAAAAV1BMVEVHcEz/OgD/OgD/OgD/OgD/OgD/OgD/OgD/OgD/OgD/OgD/OgD/OgD/OgD/OgD/OgD/OgD/OgD/OgD/OgD/OgD/OgD/OgD/OgD/OgD/OgD/OgD/OgD/OgD/maxbAAAAHHRSTlMAOZ4DJi3nBvftGwy7zNVo3RNcRk20w4eoe5JvWvIB4QAAA/5JREFUWMPNWNuypCoMbS94Q1QUUdT//85x79Y2IRG7ps6pmlQ/AWZ1FrmR1+tfk0RqrWX+H2nL5dfKdNQuo1VK2TF2pkqunUpckiJleQq2JNa2vrXVsRuqB5OjSZXbJUU3959Phq78SNbDr/rs2rEV0lYAZU08yHvsKIbIhzTuUJfHYFUBM9IGIPQhbUVtbvjXEwP9I6OkINt0GQj/VHwq1y7jdBVxyppteeitWM8jPSCxjM5VA1abU7UYb7RtzUCxTXd3ev5cFCL+5KNSDOlRs91K2RPs7O5sJ25ut32vTQzpUbdt36Pfnz4xKPHdL8VRSUlPmy0oJWK+stsz6YT4ZU8CcqSky3F7kAZ4XbL45pZZVhDSf06mgKLCvF4rQ7rzte3iLcVXxA0oxgrlBpGKqI87GLaHtECP1aKj5ogMh7YzUWRcjfB//vfB5YwcrNVvI/fbcBNJSRIedjHj6YhGaw4N0lgudyCf2SziOaExCY2FdJ5MIsNjkAgr+LeLgfmrSjyWnrYI+hC88VmjFArR42OtuQsCXhDxhHRpeaf2Q7B5czJA7pIvqr1gksLHfQW4w9X/dCW8r1zCDsoaCNweuC4p4BUw3f2uAI+10LmHtb1kNYATkkVARE7kWqEs3m5ec3VyjwGc7ev8fg/mDGBKyzirp1Aq9rhvHQJ/rcVNtsxHGk3wX1/fKek5O8hnfo7E4FrBvQUk/4vHgnEg4I6N9sDNLbEeuEEJuRFfgic+OEu7rrcQeKW80pdztJtn2lmHc1sInFbB677mQJijQHwrBP455lyZI+CGJNguZUJtTh5DDVqZvS8vd/X4lowD90lHwQZsy9JQklmJHe64uVNiBpyQjoiH6XUKhPkRiFXHd4v4Si5wUwaqWgILSxYFCoumTf+on8BRq/zQRNnqthwunP/E+gEckF442rPDUN6/AtdeQSM/JUyiBqeOLicF4X6CQ9LnvKevFUTk1hxNmd9GXZmhR6FTxqaS+f6qFqsioQZJ36+UtNIkORZq6gfSQILanXu9SdHZcaybksZ5At8nzu/oDH3DnL2ztwLjQDRPbf4BDkm32m8sjtaI5mZfsCOa8itwSPrR7iGkg3jRhXV1OAST/gn9p7tDpB9AKBWfxA9ZSFVGCn0fPF/8NuBDyTUQEzOwGAK2d0yTMajA+T73npNXHUtQqj/5uB017KHM9aTVckN9tqTE0+HjFQ0sziJe8UOWctJ3s6iZ+aBbBL3cDNYAFKmfSRGnrZwDvXkeTdYbhbXp8WLT4/5uPgX3CaIBWw5qQ6MwNUUPs0Ap+mmurVJ2XtYBDAFlCsR7vFZgC84NPyNFOy5tpL94De2/XO6SvP5CEm6Y+rfK/lf5A5RpN2/mmB9oAAAAAElFTkSuQmCC"

def listar_archivos_y_carpetas(ruta, listbox_archivos):
    listbox_archivos.delete(0, tk.END)
    archivos = os.listdir(ruta)
    for archivo in archivos:
        ruta_completa = os.path.join(ruta, archivo)
        if os.path.isdir(ruta_completa):
            listbox_archivos.insert(tk.END, archivo)
            listbox_archivos.itemconfig(tk.END, foreground='blue')
        else:
            listbox_archivos.insert(tk.END, archivo)
            listbox_archivos.itemconfig(tk.END, foreground='black')
    listbox_archivos.current_path = ruta  # type: ignore
    
def on_double_click(event):
    seleccion = event.widget.curselection()
    if seleccion:
        archivo = event.widget.get(seleccion)
        ruta_completa = os.path.join(event.widget.current_path, archivo)  # type: ignore
        abrir_archivo_y_carpeta(ruta_completa, event.widget)

def abrir_archivo_y_carpeta(ruta, listbox_archivos):
    if os.path.isdir(ruta):
        listar_archivos_y_carpetas(ruta, listbox_archivos)
    else:
        os.startfile(ruta)

def procesar_directorio(directorio):
    try:
        # Verificar si el directorio existe
        if not os.path.isdir(directorio):
            raise FileNotFoundError(f"El directorio '{directorio}' no existe.")
        
        # Listar el contenido del directorio
        contenido = os.listdir(directorio)
        
        # Filtrar solo directorios
        solo_directorios = [d for d in contenido if os.path.isdir(os.path.join(directorio, d))]
        
        if not solo_directorios:
            raise ValueError("No se encontraron subdirectorios en el directorio dado.")
        
        # Tomar el primer directorio
        primer_directorio = solo_directorios[0]
        
        # Separar el primer directorio en dos partes
        cadena = primer_directorio[:-4] if len(primer_directorio) > 4 else ""
        ultimos_cuatro = list(primer_directorio[-4:])
        
        # Crear la lista de últimos cuatro caracteres de todos los directorios
        ultimos_caracteres = set()
        for d in solo_directorios:
            if len(d) >= 4:
                ultimos_caracteres.add(d[-4:])
        
        # Ordenar la lista en orden descendente y convertirla en lista
        lista_ordenada = sorted(ultimos_caracteres, reverse=True)
        
        return lista_ordenada, cadena
    except Exception as e:
        return str(e)

#ZOOPLUS

def indicadores(current_dir_var, listbox_archivos):
    usuario = os.environ['USERNAME']
    
    try:
        directorio = f"C:\\Users\\{usuario}\\GXO\\SPCABANILLAS - Cabanillas_Zooplus\\6. Stock\\05. Indicadores Zooplus"
        current_dir_var.set(directorio)
        listar_archivos_y_carpetas(directorio, listbox_archivos)
    except Exception as e:
        messagebox.showinfo("Sistema", f"Error: {e}")

def imbalances(current_dir_var, listbox_archivos):
    usuario = os.environ['USERNAME']
    try:
        directorio = f"C:\\Users\\{usuario}\\GXO\\SPCABANILLAS - Cabanillas_Zooplus\\6. Stock\\06. Inventory Accuracy Between Systems Zooplus"
        
        current_dir_var.set(directorio)
        listar_archivos_y_carpetas(directorio, listbox_archivos)
    except Exception as e:
        messagebox.showinfo("Sistema", f"Error: {e}")

def dañados(current_dir_var, listbox_archivos):
    usuario = os.environ['USERNAME']
    try:
        directorio = f"C:\\Users\\{usuario}\\GXO\\SPCABANILLAS - Cabanillas_Zooplus\\6. Stock\\09. Dañados Zooplus"
        
        current_dir_var.set(directorio)
        listar_archivos_y_carpetas(directorio, listbox_archivos)
    except Exception as e:
        messagebox.showinfo("Sistema", f"Error: {e}")
        
def incidencias(current_dir_var, listbox_archivos):
    usuario = os.environ['USERNAME']
    try:
        directorio = f"C:\\Users\\{usuario}\\GXO\\SPCABANILLAS - Cabanillas_Zooplus\\6. Stock\\11. Anulación de Preparación"
        
        current_dir_var.set(directorio)
        listar_archivos_y_carpetas(directorio, listbox_archivos)
    except Exception as e:
        messagebox.showinfo("Sistema", f"Error: {e}")

def errores(current_dir_var, listbox_archivos):
    usuario = os.environ['USERNAME']
    try:
        directorio = f"C:\\Users\\{usuario}\\GXO\\SPCABANILLAS - Cabanillas_Zooplus\\6. Stock\\25. Reporte Errores"
        
        current_dir_var.set(directorio)
        listar_archivos_y_carpetas(directorio, listbox_archivos)
    except Exception as e:
        messagebox.showinfo("Sistema", f"Error: {e}")
        
def horas_returns(current_dir_var, listbox_archivos):
    usuario = os.environ['USERNAME']
    try:
        directorio = f"C:\\Users\\{usuario}\\GXO\\SPCABANILLAS - Cabanillas_Zooplus\\1. Gestión Operativa\\03. Devoluciones\\Control -NO TOCAR-"
        
        current_dir_var.set(directorio)
        listar_archivos_y_carpetas(directorio, listbox_archivos)
    except Exception as e:
        messagebox.showinfo("Sistema", f"Error: {e}")
        
def kpi_cancelaciones(current_dir_var, listbox_archivos):
    usuario = os.environ['USERNAME']
    try:
        directorio = f"C:\\Users\\{usuario}\\GXO\\SPCABANILLAS - Cabanillas_Zooplus\\6. Stock\\16. Analisis Stock\\DPMO Cancel"
        
        current_dir_var.set(directorio)
        listar_archivos_y_carpetas(directorio, listbox_archivos)
    except Exception as e:
        messagebox.showinfo("Sistema", f"Error: {e}")
        
def returns(current_dir_var, listbox_archivos):
    usuario = os.environ['USERNAME']
    try:
        directorio = f"C:\\Users\\{usuario}\\GXO\\SPCABANILLAS - Cabanillas_Zooplus\\6. Stock\\26. Seguimiento Returns"
    
        current_dir_var.set(directorio)
        listar_archivos_y_carpetas(directorio, listbox_archivos)
    except Exception as e:
        messagebox.showinfo("Sistema", f"Error: {e}")

def cco_zoo(current_dir_var, listbox_archivos):
    usuario = os.environ['USERNAME']
    try:
        directorio = f"C:\\Users\\{usuario}\\GXO\\SPCABANILLAS - Cabanillas_Zooplus\\6. Stock\\01. Cycle Count Zooplus"
       
        current_dir_var.set(directorio)
        listar_archivos_y_carpetas(directorio, listbox_archivos)
    except Exception as e:
        messagebox.showinfo("Sistema", f"Error: {e}")

def dangerous_la(current_dir_var, listbox_archivos):
    usuario = os.environ['USERNAME']
    try:
        directorio = f"C:\\Users\\{usuario}\\GXO\\SPCABANILLAS - Cabanillas_Zooplus\\1. Gestión Operativa\\03. Devoluciones"

        current_dir_var.set(directorio)
        listar_archivos_y_carpetas(directorio, listbox_archivos)
    except Exception as e:
        messagebox.showinfo("Sistema", f"Error: {e}")

def ultimas_unidades(current_dir_var, listbox_archivos):
    usuario = os.environ['USERNAME']
    try:
        directorio = f"C:\\Users\\{usuario}\\GXO\\SPCABANILLAS - Cabanillas_Zooplus\\6. Stock\\23. Ultimas Unidades"

        current_dir_var.set(directorio)
        listar_archivos_y_carpetas(directorio, listbox_archivos)
    except Exception as e:
        messagebox.showinfo("Sistema", f"Error: {e}")

def donaciones(current_dir_var, listbox_archivos):
    usuario = os.environ['USERNAME']
    try:
        directorio = f"C:\\Users\\{usuario}\\GXO\\SPCABANILLAS - Cabanillas_Zooplus\\1. Gestión Operativa\\14. Donaciones"

        current_dir_var.set(directorio)
        listar_archivos_y_carpetas(directorio, listbox_archivos)
    except Exception as e:
        messagebox.showinfo("Sistema", f"Error: {e}")

def cuadrantes(current_dir_var, listbox_archivos):
    usuario = os.environ['USERNAME']
    try:
        directorio = f"C:\\Users\\{usuario}\\GXO\\SPCABANILLAS - Cabanillas_Zooplus\\6. Stock\\24. Cuadrantes"

        current_dir_var.set(directorio)
        listar_archivos_y_carpetas(directorio, listbox_archivos)
    except Exception as e:
        messagebox.showinfo("Sistema", f"Error: {e}")

#ELECTROLUX

def seleccionar_ano():
    usuario = os.environ['USERNAME']
    directorio = f"C:\\Users\\{usuario}\\GXO\\SPCABANILLAS - Cabanillas_Electrolux\\6. Stock\\1. FICHEROS HISTORICOS"
    lista_anos, direccion = procesar_directorio(directorio)
    #print("Lista:", lista_anos)
    #print("Cadena:", direccion)
    texto_ajustado = ajustar_texto(direccion, ancho_maximo=30)
    app_ano = tk.Tk()
    app_ano.title("Seleccionar Año")
    app_ano.geometry("300x200")
    
    label = tk.Label(
        app_ano,
        text=f"{texto_ajustado}",
        foreground="black",
        font=("Arial", 12, "bold"),
        
    )
    label.pack(pady=10)

    combo = ttk.Combobox(
        app_ano,
        values=lista_anos, # type: ignore
        )
    
    combo.pack(pady=10)
    
    combo.current_path = ""  # type: ignore
    combo.bind("<Double-1>", on_double_click)
    
    button_ok = tk.Button(
        app_ano,
        text="OK",
        command=lambda: electrolux(combo.get()),
        width=18
    )
    button_ok.pack(pady=10)
    
    button_exit = tk.Button( 
        app_ano,
        text="Salir",
        command=app_ano.destroy,
        width=18,
        foreground="red"        
        
    )
    button_exit.pack(pady=10)
    

    
    app_ano.mainloop()
    
def errores_elux(listbox_archivos, current_dir_var, ano):
    year = ano
    usuario = os.environ['USERNAME']
    try:
        directorio = f"C:\\Users\\{usuario}\\GXO\\SPCABANILLAS - Cabanillas_Electrolux\\6. Stock\\1. FICHEROS HISTORICOS"
        ano_trash, carpeta = procesar_directorio(directorio)
        directorio = f"C:\\Users\\{usuario}\\GXO\\SPCABANILLAS - Cabanillas_Electrolux\\6. Stock\\1. FICHEROS HISTORICOS\\{carpeta}{year}\\09. REPORTE ERRORES"

        current_dir_var.set(directorio)
        listar_archivos_y_carpetas(directorio, listbox_archivos)
    except Exception as e:
        messagebox.showinfo("Sistema", f"Error: {e}")
        
def discrepancias(listbox_archivos, current_dir_var, ano):
    year = ano
    usuario = os.environ['USERNAME']
    try:
        directorio = f"C:\\Users\\{usuario}\\GXO\\SPCABANILLAS - Cabanillas_Electrolux\\6. Stock\\1. FICHEROS HISTORICOS"
        ano_trash, carpeta = procesar_directorio(directorio)
        directorio = f"C:\\Users\\{usuario}\\GXO\\SPCABANILLAS - Cabanillas_Electrolux\\6. Stock\\1. FICHEROS HISTORICOS\\{carpeta}{year}\\12. DISCREPANCIAS"

        current_dir_var.set(directorio)
        listar_archivos_y_carpetas(directorio, listbox_archivos)
    except Exception as e:
        messagebox.showinfo("Sistema", f"Error: {e}")

def cco_elux(listbox_archivos, current_dir_var, ano):
    year = ano
    usuario = os.environ['USERNAME']
    try:
        directorio = f"C:\\Users\\{usuario}\\GXO\\SPCABANILLAS - Cabanillas_Electrolux\\6. Stock\\1. FICHEROS HISTORICOS"
        ano_trash, carpeta = procesar_directorio(directorio)
        directorio = f"C:\\Users\\{usuario}\\GXO\\SPCABANILLAS - Cabanillas_Electrolux\\6. Stock\\1. FICHEROS HISTORICOS\\{carpeta}{year}\\04. Cycle Count ELECTROLUX"

        current_dir_var.set(directorio)
        listar_archivos_y_carpetas(directorio, listbox_archivos)
    except Exception as e:
        messagebox.showinfo("Sistema", f"Error: {e}")

#OPERACIONES CABANILLAS

def stock(listbox_archivos, current_dir_var):
    usuario = os.environ['USERNAME']
    try:
        directorio = f"C:\\Users\\{usuario}\\GXO\\SPCABANILLAS - Cabanillas_Operaciones\\6. Stock"
        
        current_dir_var.set(directorio)
        listar_archivos_y_carpetas(directorio, listbox_archivos)
    except Exception as e:
        messagebox.showinfo("Sistema", f"Error: {e}")
        
def cabanillas(listbox_archivos, current_dir_var):
    usuario = os.environ['USERNAME']
    try:
        directorio = f"C:\\Users\\{usuario}\\GXO\\SPCABANILLAS - Cabanillas_Operaciones\\1. Cabanillas Board"
        
        current_dir_var.set(directorio)
        listar_archivos_y_carpetas(directorio, listbox_archivos)
    except Exception as e:
        messagebox.showinfo("Sistema", f"Error: {e}")


#VENTANAS
  
def zooplus():
    
    app2 = tk.Toplevel()
    app2.title("Zooplus")
    app2.geometry("400x680")
    
    icon_zooplus = "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"

    icon_path2 = os.path.join(tempfile.gettempdir(), "app2_icon.ico")
    with open(icon_path2, "wb") as icon2_file:
        icon2_file.write(b64decode(icon_zooplus))
    
    app2.iconbitmap(icon_path2)
        
    current_dir_var = tk.StringVar()

    label = ttk.Label(
        app2,
        text="Tareas Disponibles",
        foreground="black",
        font=("Arial", 18, "bold"),
        
    )
    label.place(x=85, y=10)
    
    global listbox_archivos
    listbox_archivos = Listbox(
        app2,
        width=40,
        height=15
    )
    listbox_archivos.place(x=65, y=360)
    listbox_archivos.bind("<Double-1>", on_double_click)
   

    button_indicadores = tk.Button(
        app2,
        text="Indicadores",
        command=partial(indicadores, current_dir_var, listbox_archivos),
        width=18
    )
    button_indicadores.place(x=50, y=50)

    button_salir = tk.Button(
        app2,
        text="Salir",
        command=app2.destroy,
        width=18,
        foreground="red"        
        
    )
    button_salir.place(x=230, y=625)
    
    
    button2 = tk.Button(
        app2,
        text="Imbalances",
        command=partial(imbalances, current_dir_var, listbox_archivos),
        width=18
    )
    button2.place(x=50, y=90)
    
    button3 = tk.Button(
        app2,
        text="Revisión Dañados",
        command=partial(dañados, current_dir_var, listbox_archivos),
        width=18
    )
    button3.place(x=50, y=130)
    
    button4 = tk.Button(
        app2,
        text="Gestión incidencias",
        command=partial(incidencias, current_dir_var, listbox_archivos),
        width=18
    )
    button4.place(x=50, y=170)
    
    button6 = tk.Button(
        app2,
        text="Errores",
        command=partial(errores, current_dir_var, listbox_archivos),
        width=18
    )
    button6.place(x=50, y=210)
    
    button7 = tk.Button(
        app2,
        text="Horas Returns",
        command=partial(horas_returns, current_dir_var, listbox_archivos),
        width=18
    )
    button7.place(x=225, y=50)
    
    button8 = tk.Button(
        app2,
        text="KPI cancelaciones",
        command=partial(kpi_cancelaciones, current_dir_var, listbox_archivos),
        width=18
    )
    button8.place(x=225, y=90)
    
    button9 = tk.Button(
        app2,
        text="Returns",
        command=partial(returns, current_dir_var, listbox_archivos),
        width=18
    )
    button9.place(x=225, y=130)
    
    button_cco_zoo = tk.Button(
        app2,
        text="Conteo Cíclico",
        command=partial(cco_zoo, current_dir_var, listbox_archivos),
        width=18
    )
    button_cco_zoo.place(x=225, y=170)
    
    button_dangerous_la = tk.Button(
        app2,
        text="Dangerous LA",
        command=partial(dangerous_la, current_dir_var, listbox_archivos),
        width=18
    )
    button_dangerous_la.place(x=225, y=210)
    
    button_ultimas_unidades = tk.Button(
        app2,
        text="Ultimas Unidades",
        command=partial(ultimas_unidades, current_dir_var, listbox_archivos),
        width=18
    )
    button_ultimas_unidades.place(x=50, y=250)
    
    button_donaciones = tk.Button(
        app2,
        text="Donaciones",
        command=partial(donaciones, current_dir_var, listbox_archivos),
        width=18
    )
    button_donaciones.place(x=50, y=290)
    
    button_cuadrantes = tk.Button(
        app2,
        text="Cuadrantes",
        command=partial(cuadrantes, current_dir_var, listbox_archivos),
        width=18
    )
    button_cuadrantes.place(x=225, y=250)

    zooplus_img = "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"
    
    image = tk.PhotoImage(data=b64decode(zooplus_img))
    label2 = ttk.Label(
        app2,
        image=image,
        #text="ZOOPLUS",
        #background="white",
        
    )
    label2.place(x=240, y=320)
    
    app2.mainloop()
    

def electrolux(ano):
    
    app4 = tk.Toplevel(app)
    app4.title("Electrolux")
    app4.geometry("400x400")
    
    elec_ico = "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"
    
    icon_path = os.path.join(tempfile.gettempdir(), "app_icon.ico")
    with open(icon_path, "wb") as icon_file:
        icon_file.write(b64decode(elec_ico))
    
    app4.iconbitmap(icon_path)
    
    
    current_dir_var = tk.StringVar()
    
    label = ttk.Label(
        app4,
        text="Tareas Disponibles",
        foreground="black",
        font=("Arial", 18, "bold"),
        
    )
    label.place(x=80, y=10)
    
    listbox_archivos = Listbox(
    app4,
    width=50,
    height=5
    )
    listbox_archivos.place(x=50, y=250)
    
    listbox_archivos.current_path = ""  # type: ignore
    listbox_archivos.bind("<Double-1>", on_double_click)
      
    button6 = tk.Button(
        app4,
        text="Errores",
        command=partial(errores_elux, listbox_archivos, current_dir_var, ano),
        width=18
    )
    button6.place(x=30, y=50)
    
    button9 = tk.Button(
        app4,
        text="Discrepancias",
        command=partial(discrepancias, listbox_archivos, current_dir_var, ano),
        width=18
    )
    button9.place(x=230, y=50)
    
    button2 = tk.Button(
        app4,
        text="Conteo Cíclico",
        command=partial(cco_elux, listbox_archivos, current_dir_var, ano),
        width=18
    )
    button2.place(x=30, y=90)
    elux_img = "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"
    
    image = tk.PhotoImage(data=b64decode(elux_img))
    label2 = ttk.Label(
        app4,
        image=image,
               
    )
    label2.place(x=220, y=200)
    
    button11 = tk.Button(
        app4,
        text="Salir",
        command=app4.destroy,
        width=18,
        foreground="red"

    )
    button11.place(x=250, y=350)
    
    app4.mainloop()

def operaciones():
    
    app5 = tk.Toplevel(app)
    app5.title("Operaciones")
    app5.geometry("400x400")
        
    current_dir_var = tk.StringVar()
    icon_zooplus = "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"

    icon_path = os.path.join(tempfile.gettempdir(), "app_icon.ico")
    with open(icon_path, "wb") as icon_file:
        icon_file.write(b64decode(icon_zooplus))
    
    app5.iconbitmap(icon_path)
    
    label = ttk.Label(
        app5,
        text="Tareas Disponibles",
        foreground="black",
        font=("Arial", 18, "bold"),
        
    )
    label.place(x=70, y=10)

    listbox_archivos = Listbox(
    app5,
    width=50,
    height=5
    )
    listbox_archivos.place(x=50, y=250)
    listbox_archivos.current_path = ""  # type: ignore
    listbox_archivos.bind("<Double-1>", on_double_click)
    
    button6 = tk.Button(
        app5,
        text="Stock",
        command=partial(stock, listbox_archivos, current_dir_var),
        width=18
    )
    button6.place(x=50, y=50)
    
    button = tk.Button(
    app5,
    text="Cabanillas",
    command=partial(cabanillas, listbox_archivos, current_dir_var),
    width=18
    )
    button.place(x=220, y=50)
    
    cab_img = "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"
    
    image = tk.PhotoImage(data=b64decode(cab_img))
    label2 = ttk.Label(
        app5,
        image=image,
               
    )
    label2.place(x=220, y=135)
    
    button11 = tk.Button(
        app5,
        text="Salir",
        command=app5.destroy,
        foreground="red",
        width=18
        
             
    )
    button11.place(x=245, y=350)
    
    app5.mainloop()

app = tk.Tk()

icon_main ="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"

icon_path = os.path.join(tempfile.gettempdir(), "app_icon.ico")
with open(icon_path, "wb") as icon_file:
    icon_file.write(b64decode(icon_main))

app.geometry("450x300")
app.title("Trabajos diarios Stock")

app.iconbitmap(icon_path)

label = ttk.Label(
    app,
    text="Trabajos Diarios Stock",
    foreground="black",
    font=("Helvetica", 20, "bold"),
)
label.place(x=60, y=40)

button_zooplus = tk.Button(
    app,
    text="Zooplus",
    command=zooplus,
    width=12
   
)
button_zooplus.place(x=50, y=100)

button_electrolux = tk.Button(
    app,
    text="Electrolux",
    command=seleccionar_ano, #type: ignore
    width=12
    
)
button_electrolux.place(x=250, y=100)

button_operaciones = tk.Button(
    app,
    text="Operaciones",
    command=operaciones,
    width=12
   
)
button_operaciones.place(x=250, y=140)

raw_image_data = b64decode(raw_image)
with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as temp_image_file:
    temp_image_file.write(raw_image_data)
    temp_image_path = temp_image_file.name

image = Image.open(temp_image_path)
photo = ImageTk.PhotoImage(image)

label2 = tk.Label(app, image=photo, text="")#type: ignore
label2.place(x=275, y=185)

button_salir = tk.Button(
    app,
    text="Salir",
    command=app.destroy,
    width=12,
    foreground="red"
    
)
button_salir.place(x=270, y=250)

app.mainloop()
