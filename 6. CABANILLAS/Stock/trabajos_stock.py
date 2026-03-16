from functools import partial
from tkinter import ttk, messagebox
import tkinter as tk
import os
from base64 import b64decode



def imbalances(combo_value):
    try:
        if combo_value == "Javi":
            os.startfile(r"C:\Users\jgmeras\GXO\SPCABANILLAS - Cabanillas_Zooplus\6. Stock\06. Inventory Accuracy Between Systems Zooplus\2024\Inventory Accuracy Between Systems Zooplus 2024.xlsx")
        elif combo_value == "Yohan":
            os.startfile(r"C:\Users\yrodriguez\GXO\SPCABANILLAS - Cabanillas_Zooplus\6. Stock\06. Inventory Accuracy Between Systems Zooplus\2024\Inventory Accuracy Between Systems Zooplus 2024.xlsx")
    except:
        messagebox.showinfo("Sistema", "Archivo no encontrado")
        
def indicadores(combo_value):
    try:
        if combo_value == "Javi":
            os.startfile(r"C:\Users\jgmeras\GXO\SPCABANILLAS - Cabanillas_Zooplus\6. Stock\05. Indicadores Zooplus\2024\Indicadores Zooplus 2024.xlsx")
        elif combo_value == "Yohan":
            os.startfile(r"C:\Users\yrodriguez\GXO\SPCABANILLAS - Cabanillas_Zooplus\6. Stock\05. Indicadores Zooplus\2024\Indicadores Zooplus 2024.xlsx")
    except:
        messagebox.showinfo("Sistema", "Archivo no encontrado")
        
def dañados(combo_value):
    try:
        if combo_value == "Javi":
            os.startfile(r"C:\Users\jgmeras\GXO\SPCABANILLAS - Cabanillas_Zooplus\6. Stock\09. Dañados Zooplus\2024\Control Dañados 2024.xlsx")
        elif combo_value == "Yohan":
            os.startfile(r"C:\Users\yrodriguez\GXO\SPCABANILLAS - Cabanillas_Zooplus\6. Stock\09. Dañados Zooplus\2024\Control Dañados 2024.xlsx")
    except:
        messagebox.showinfo("Sistema", "Archivo no encontrado")
        
def sustituciones(combo_value):
    try:
        if combo_value == "Javi":
            os.startfile(r"C:\Users\jgmeras\GXO\SPCABANILLAS - Cabanillas_Zooplus\6. Stock\11. Anulación de Preparación\2024\Reporte Equipo Incidencias 2024.xlsx")
        elif combo_value == "Yohan":
            os.startfile(r"C:\Users\yrodriguez\GXO\SPCABANILLAS - Cabanillas_Zooplus\6. Stock\11. Anulación de Preparación\2024\Reporte Equipo Incidencias 2024.xlsx")
    except:
        messagebox.showinfo("Sistema", "Archivo no encontrado")
        
        
def cancelaciones(combo_value):
    try:
        if combo_value == "Javi":
            os.startfile(r"C:\Users\jgmeras\GXO\SPCABANILLAS - Cabanillas_Zooplus\6. Stock\11. Anulación de Preparación\2024\Anulación de Preparación 2024.xlsx")
        elif combo_value == "Yohan":
            os.startfile(r"C:\Users\yrodriguez\GXO\SPCABANILLAS - Cabanillas_Zooplus\6. Stock\11. Anulación de Preparación\2024\Anulación de Preparación 2024.xlsx")
    except:
        messagebox.showinfo("Sistema", "Archivo no encontrado")
        
def errores(combo_value):
    try:
        if combo_value == "Javi":
            os.startfile(r"C:\Users\jgmeras\GXO\SPCABANILLAS - Cabanillas_Zooplus\6. Stock\25. Reporte Errores\2024\Reporte Errores Zooplus.xlsx")
        elif combo_value == "Yohan":
            os.startfile(r"C:\Users\yrodriguez\GXO\SPCABANILLAS - Cabanillas_Zooplus\6. Stock\25. Reporte Errores\2024\Reporte Errores Zooplus.xlsx")
    except:
        messagebox.showinfo("Sistema", "Archivo no encontrado")
        
def horas_returns(combo_value):
    try:
        if combo_value == "Javi":
            os.startfile(r"C:\Users\jgmeras\GXO\SPCABANILLAS - Cabanillas_Zooplus\1. Gestión Operativa\03. Devoluciones\Control -NO TOCAR-\Qty-Avrg Returns.xlsx")
        elif combo_value == "Yohan":
            os.startfile(r"C:\Users\yrodriguez\GXO\SPCABANILLAS - Cabanillas_Zooplus\1. Gestión Operativa\03. Devoluciones\Control -NO TOCAR-\Qty-Avrg Returns.xlsx")
    except:
        messagebox.showinfo("Sistema", "Archivo no encontrado")
        
def kpi_cancelaciones(combo_value):
    try:
        if combo_value == "Javi":
            os.startfile(r"C:\Users\jgmeras\GXO\SPCABANILLAS - Cabanillas_Zooplus\6. Stock\16. Analisis Stock\DPMO Cancel\Cancellations DPMO.xlsx")
        elif combo_value == "Yohan":
            os.startfile(r"C:\Users\yrodriguez\GXO\SPCABANILLAS - Cabanillas_Zooplus\6. Stock\16. Analisis Stock\DPMO Cancel\Cancellations DPMO.xlsx")
    except:
        messagebox.showinfo("Sistema", "Archivo no encontrado")
        
def returns_stock(combo_value):
    try:
        if combo_value == "Javi":
            os.startfile(r"C:\Users\jgmeras\GXO\SPCABANILLAS - Cabanillas_Zooplus\6. Stock\26. Seguimiento Returns\Seguimiento Returns.xlsx")
        elif combo_value == "Yohan":
            os.startfile(r"C:\Users\yrodriguez\GXO\SPCABANILLAS - Cabanillas_Zooplus\6. Stock\26. Seguimiento Returns\Seguimiento Returns.xlsx")
    except:
        messagebox.showinfo("Sistema", "Archivo no encontrado")
        
def returns_staff(combo_value):
    try:
        if combo_value == "Javi":
            os.startfile(r"C:\Users\jgmeras\GXO\SPCABANILLAS - Cabanillas_Zooplus\6. Stock\26. Seguimiento Returns\Seguimiento Staff.xlsx")
        elif combo_value == "Yohan":
            os.startfile(r"C:\Users\yrodriguez\GXO\SPCABANILLAS - Cabanillas_Zooplus\6. Stock\26. Seguimiento Returns\Seguimiento Staff.xlsx")
    except:
        messagebox.showinfo("Sistema", "Archivo no encontrado")
        
def errores_nike(combo_value):
    try:
        if combo_value == "Javi":
            os.startfile(r"C:\Users\jgmeras\GXO\SPCABANILLAS - Cabanillas_Nike\6. Stock\13. Reporte Errores\2024\Reporte Errores Nike 2024.xlsx")
        elif combo_value == "Yohan":
            os.startfile(r"C:\Users\yrodriguez\GXO\SPCABANILLAS - Cabanillas_Nike\6. Stock\13. Reporte Errores\2024\Reporte Errores Nike 2024.xlsx")
    except:
        messagebox.showinfo("Sistema", "Archivo no encontrado")

def returns_general(combo_value):
    try:
        if combo_value == "Javi":
            os.startfile(r"C:\Users\jgmeras\GXO\SPCABANILLAS - Cabanillas_Nike\6. Stock\16. Análisis\Status diario\V Nike RSO.xlsx")
        elif combo_value == "Yohan":
            os.startfile(r"C:\Users\yrodriguez\GXO\SPCABANILLAS - Cabanillas_Nike\6. Stock\16. Análisis\Status diario\V Nike RSO.xlsx")
    except:
        messagebox.showinfo("Sistema", "Archivo no encontrado")

def returns_especifico(combo_value):
    try:
        if combo_value == "Javi":
            os.startfile(r"C:\Users\jgmeras\GXO\SPCABANILLAS - Cabanillas_Nike\6. Stock\16. Análisis\Status diario\Status diario Returns.xlsx")
        elif combo_value == "Yohan":
            os.startfile(r"C:\Users\yrodriguez\GXO\SPCABANILLAS - Cabanillas_Nike\6. Stock\16. Análisis\Status diario\Status diario Returns.xlsx")
    except:
        messagebox.showinfo("Sistema", "Archivo no encontrado")

def errores_elux(combo_value):
    try:
        if combo_value == "Javi":
            os.startfile(r"C:\Users\jgmeras\GXO\SPCABANILLAS - Cabanillas_Electrolux\6. Stock\1. FICHEROS HISTORICOS\PLANTILLAS INVENTARIO ROTATIVOS 2024\09. REPORTE ERRORES\Reporte Errores Electrolux.xlsx")
        elif combo_value == "Yohan":
            os.startfile(r"C:\Users\yrodriguez\GXO\SPCABANILLAS - Cabanillas_Electrolux\6. Stock\1. FICHEROS HISTORICOS\PLANTILLAS INVENTARIO ROTATIVOS 2024\09. REPORTE ERRORES\Reporte Errores Electrolux.xlsx")
    except:
        messagebox.showinfo("Sistema", "Archivo no encontrado")
        
def discrepancias(combo_value):
    try:
        if combo_value == "Javi":
            os.startfile(r"C:\Users\jgmeras\GXO\SPCABANILLAS - Cabanillas_Electrolux\6. Stock\1. FICHEROS HISTORICOS\PLANTILLAS INVENTARIO ROTATIVOS 2024\12. DISCREPANCIAS\Discrepancias.xlsx")
        elif combo_value == "Yohan":
            os.startfile(r"C:\Users\yrodriguez\GXO\SPCABANILLAS - Cabanillas_Electrolux\6. Stock\1. FICHEROS HISTORICOS\PLANTILLAS INVENTARIO ROTATIVOS 2024\12. DISCREPANCIAS\Discrepancias.xlsx")
    except:
        messagebox.showinfo("Sistema", "Archivo no encontrado")

def vacaciones_stock(combo_value):
    try:
        if combo_value == "Javi":
            os.startfile(r"C:\Users\jgmeras\GXO\SPCABANILLAS - Cabanillas_Operaciones\6. Stock\2024\Vacaciones Stock 2024.xlsm")
        elif combo_value == "Yohan":
            os.startfile(r"C:\Users\yrodriguez\GXO\SPCABANILLAS - Cabanillas_Operaciones\6. Stock\2024\Vacaciones Stock 2024.xlsm")
    except:
        messagebox.showinfo("Sistema", "Archivo no encontrado")

def horas_extras_stock(combo_value):
    try:
        if combo_value == "Javi":
            os.startfile(r"C:\Users\jgmeras\GXO\SPCABANILLAS - Cabanillas_Operaciones\6. Stock\2024\Horas Extras 2024.xlsx")
        elif combo_value == "Yohan":
            os.startfile(r"C:\Users\yrodriguez\GXO\SPCABANILLAS - Cabanillas_Operaciones\6. Stock\2024\Horas Extras 2024.xlsx")
    except:
        messagebox.showinfo("Sistema", "Archivo no encontrado")

def vacaciones_cab(combo_value):
    try:
        if combo_value == "Javi":
            os.startfile(r"C:\Users\jgmeras\GXO\SPCABANILLAS - Cabanillas_Operaciones\1. Cabanillas Board\Vacaciones Cabanillas 2024.xlsm")
        elif combo_value == "Yohan":
            os.startfile(r"C:\Users\yrodriguez\GXO\SPCABANILLAS - Cabanillas_Operaciones\1. Cabanillas Board\Vacaciones Cabanillas 2024.xlsm")
    except:
        messagebox.showinfo("Sistema", "Archivo no encontrado")    

def cabanillas_sc(combo_value):
    try:
        if combo_value == "Javi":
            os.startfile(r"C:\Users\jgmeras\GXO\SPCABANILLAS - Cabanillas_Operaciones\1. Cabanillas Board\Cabanillas SC 2024.xlsx")
        elif combo_value == "Yohan":
            os.startfile(r"C:\Users\yrodriguez\GXO\SPCABANILLAS - Cabanillas_Operaciones\1. Cabanillas Board\Cabanillas SC 2024.xlsx")
    except:
        messagebox.showinfo("Sistema", "Archivo no encontrado")

def zooplus(combo):
    combo_value = combo.get()
    app2 = tk.Toplevel()
    app2.title("Zooplus")
    app2.geometry("400x400")
    
    label = ttk.Label(
        app2,
        text="Tareas Disponibles",
        foreground="black",
        font=("Arial", 14)
    )
    label.place(x=75, y=10)
    
    button = ttk.Button(
        app2,
        text="Indicadores",
        command=partial(indicadores, combo_value)
    )
    button.place(x=50, y=50)
    
    button2 = ttk.Button(
        app2,
        text="Imbalances",
        command=partial(imbalances, combo_value)
    )
    button2.place(x=50, y=90)
    
    button3 = ttk.Button(
        app2,
        text="Revisión Dañados",
        command=partial(dañados, combo_value)
    )
    button3.place(x=50, y=130)
    
    button4 = ttk.Button(
        app2,
        text="Sustituciones",
        command=partial(sustituciones, combo_value)
    )
    button4.place(x=50, y=170)
    
    button5 = ttk.Button(
        app2,
        text="Cancelaciones Operaciones",
        command=partial(cancelaciones, combo_value)
    )
    button5.place(x=50, y=210)
    
    button6 = ttk.Button(
        app2,
        text="Errores",
        command=partial(errores, combo_value)
    )
    button6.place(x=50, y=250)
    
    button7 = ttk.Button(
        app2,
        text="Horas Returns",
        command=partial(horas_returns, combo_value)
    )
    button7.place(x=225, y=50)
    
    button8 = ttk.Button(
        app2,
        text="KPI cancelaciones",
        command=partial(kpi_cancelaciones, combo_value)
    )
    button8.place(x=225, y=90)
    
    button9 = ttk.Button(
        app2,
        text="Returns Stock",
        command=partial(returns_stock, combo_value)
    )
    button9.place(x=225, y=130)
    
    button10 = ttk.Button(
        app2,
        text="Returns Staff",
        command=partial(returns_staff, combo_value)
    )
    button10.place(x=225, y=170)
    
    zooplus_img = "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"
    
    image = tk.PhotoImage(data=b64decode(zooplus_img))
    label2 = ttk.Label(
        app2,
        image=image,
        #text="ZOOPLUS",
        #background="white",
        
    )
    label2.place(x=250, y=230)
    
    
    button11 = ttk.Button(
        app2,
        text="Salir",
        command=app2.destroy    
    )
    button11.place(x=200, y=300)
    app2.mainloop()
    
def nike(combo):
    combo_value = combo.get()
    app3 = tk.Toplevel()
    app3.title("Nike")
    app3.geometry("300x300")
    
    label = ttk.Label(
        app3,
        text="Tareas Disponibles",
        foreground="black",
        font=("Arial", 14)
    )
    label.place(x=50, y=10)
 
    
    button6 = ttk.Button(
        app3,
        text="Errores",
        command=partial(errores_nike, combo_value)
    )
    button6.place(x=50, y=50)
    
    button9 = ttk.Button(
        app3,
        text="Returns Stock",
        command=partial(returns_general, combo_value)
    )
    button9.place(x=50, y=90)
    
    button10 = ttk.Button(
        app3,
        text="Returns Staff",
        command=partial(returns_especifico, combo_value)
    )
    button10.place(x=175, y=50)
    
    nike_img = "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"
    
    image = tk.PhotoImage(data=b64decode(nike_img))
    label2 = ttk.Label(
        app3,
        image=image,
        text="NIKE",
        
    )
    label2.place(x=130, y=175)
    
    button11 = ttk.Button(
        app3,
        text="Salir",
        command=app3.destroy    
    )
    button11.place(x=175, y=250)
    app3.mainloop()
    
def electrolux(combo):
    combo_value = combo.get()
    app4 = tk.Toplevel()
    app4.title("Electrolux")
    app4.geometry("250x300")
    
    label = ttk.Label(
        app4,
        text="Tareas Disponibles",
        foreground="black",
        font=("Arial", 14)
    )
    label.place(x=50, y=10)
 
    
    button6 = ttk.Button(
        app4,
        text="Errores",
        command=partial(errores_elux, combo_value)
    )
    button6.place(x=30, y=50)
    
    button9 = ttk.Button(
        app4,
        text="Discrepancias",
        command=partial(discrepancias, combo_value)
    )
    button9.place(x=130, y=50)
    
    elux_img = "iVBORw0KGgoAAAANSUhEUgAAAHgAAABDCAMAAABgBzGOAAAAIGNIUk0AAHomAACAhAAA+gAAAIDoAAB1MAAA6mAAADqYAAAXcJy6UTwAAALZUExURQAAAAApZAApZAApZAApZAApZAApZAApZAApZAApZAApZAApZAApZAApZAApZAApZAApZAApZAApZAApZAApZAApZAApZAApZAApZAApZAApZAApZAApZAApZAApZAApZAApZAApZAApZAApZAApZAApZAApZAApZAApZAApZAApZAApZAApZAApZAApZAApZAApZAApZAApZAApZAApZAApZAApZAApZAApZAApZAApZAApZAApZAApZAApZAApZAApZAApZAApZAApZAApZAApZAApZAApZAApZAApZAApZAApZAApZAApZAApZAApZAApZAApZAApZAApZAApZAApZAApZAApZAApZAApZAApZAApZAApZAApZAApZAApZAApZAApZAApZAApZAApZAApZAApZAApZAApZAApZAApZAApZAApZAApZAApZAApZAApZAApZAApZAApZAApZAApZAApZAApZAApZAApZAApZAApZAApZAApZAApZAApZAApZAApZAApZAApZAApZAApZAApZAApZAApZAApZAApZAApZAApZAApZAApZAApZAApZAApZAApZAApZAApZAApZAApZAApZAApZAApZAApZAApZAApZAApZAApZAApZAApZAApZAApZAApZAApZAApZAApZAApZAApZAApZAApZAApZAApZAApZAApZAApZAApZAApZAApZAApZAApZAApZAApZAApZAApZAApZAApZAApZAApZAApZAApZAApZAApZAApZAApZAApZAApZAApZAApZAApZAApZAApZAApZAApZAApZAApZAApZAApZAApZAApZAApZAApZAApZAApZAApZAApZAApZAApZAApZAApZAApZAApZAApZAApZAApZAApZAApZAApZAApZAApZAApZAApZAApZAApZAApZAApZAApZAApZAApZAApZAApZAApZP///08f+vEAAADxdFJOUwAAAxMWFAQgqMjHycqyJynZ9NSwl46Ws/L85jLW6KBQCgECJc2ZkN/j+7pIMNphBTmn9veYHlrvgPD6Cfl8/rYcQOVgD5z9S1JR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"
    
    image = tk.PhotoImage(data=b64decode(elux_img))
    label2 = ttk.Label(
        app4,
        image=image,
        
    )
    label2.place(x=110, y=175)
    
    button11 = ttk.Button(
        app4,
        text="Salir",
        command=app4.destroy    
    )
    button11.place(x=125, y=250)
    app4.mainloop()

def operaciones(combo):
    combo_value = combo.get()
    app5 = tk.Toplevel()
    app5.title("Operaciones")
    app5.geometry("250x300")
    
    label = ttk.Label(
        app5,
        text="Tareas Disponibles",
        foreground="black",
        font=("Arial", 14)
    )
    label.place(x=50, y=10)
 
    
    button6 = ttk.Button(
        app5,
        text="Vacaciones Stock",
        command=partial(vacaciones_stock, combo_value)
    )
    button6.place(x=30, y=50)
    
    button9 = ttk.Button(
        app5,
        text="Horas Extras Stock",
        command=partial(horas_extras_stock, combo_value)
    )
    button9.place(x=100, y=50)
    
    button = ttk.Button(
    app5,
    text="Cabanillas SC 2024",
    command=partial(cabanillas_sc, combo_value)
    )
    button.place(x=50, y=90)
    
    button2 = ttk.Button(
    app5,
    text="Vacaciones Cabanillas 2024",
    command=partial(vacaciones_cab, combo_value)
    )
    button2.place(x=100, y=90)
    
    cab_img = "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"
    
    image = tk.PhotoImage(data=b64decode(cab_img))
    label2 = ttk.Label(
        app5,
        image=image,
        
    )
    label2.place(x=110, y=175)
    
    button11 = ttk.Button(
        app5,
        text="Salir",
        command=app5.destroy    
    )
    button11.place(x=125, y=250)
    app5.mainloop()  

app = tk.Tk()

style = ttk.Style()
raw_image = "iVBORw0KGgoAAAANSUhEUgAAAHwAAAAuCAMAAADdho1wAAAAV1BMVEVHcEz/OgD/OgD/OgD/OgD/OgD/OgD/OgD/OgD/OgD/OgD/OgD/OgD/OgD/OgD/OgD/OgD/OgD/OgD/OgD/OgD/OgD/OgD/OgD/OgD/OgD/OgD/OgD/OgD/maxbAAAAHHRSTlMAOZ4DJi3nBvftGwy7zNVo3RNcRk20w4eoe5JvWvIB4QAAA/5JREFUWMPNWNuypCoMbS94Q1QUUdT//85x79Y2IRG7ps6pmlQ/AWZ1FrmR1+tfk0RqrWX+H2nL5dfKdNQuo1VK2TF2pkqunUpckiJleQq2JNa2vrXVsRuqB5OjSZXbJUU3959Phq78SNbDr/rs2rEV0lYAZU08yHvsKIbIhzTuUJfHYFUBM9IGIPQhbUVtbvjXEwP9I6OkINt0GQj/VHwq1y7jdBVxyppteeitWM8jPSCxjM5VA1abU7UYb7RtzUCxTXd3ev5cFCL+5KNSDOlRs91K2RPs7O5sJ25ut32vTQzpUbdt36Pfnz4xKPHdL8VRSUlPmy0oJWK+stsz6YT4ZU8CcqSky3F7kAZ4XbL45pZZVhDSf06mgKLCvF4rQ7rzte3iLcVXxA0oxgrlBpGKqI87GLaHtECP1aKj5ogMh7YzUWRcjfB//vfB5YwcrNVvI/fbcBNJSRIedjHj6YhGaw4N0lgudyCf2SziOaExCY2FdJ5MIsNjkAgr+LeLgfmrSjyWnrYI+hC88VmjFArR42OtuQsCXhDxhHRpeaf2Q7B5czJA7pIvqr1gksLHfQW4w9X/dCW8r1zCDsoaCNweuC4p4BUw3f2uAI+10LmHtb1kNYATkkVARE7kWqEs3m5ec3VyjwGc7ev8fg/mDGBKyzirp1Aq9rhvHQJ/rcVNtsxHGk3wX1/fKek5O8hnfo7E4FrBvQUk/4vHgnEg4I6N9sDNLbEeuEEJuRFfgic+OEu7rrcQeKW80pdztJtn2lmHc1sInFbB677mQJijQHwrBP455lyZI+CGJNguZUJtTh5DDVqZvS8vd/X4lowD90lHwQZsy9JQklmJHe64uVNiBpyQjoiH6XUKhPkRiFXHd4v4Si5wUwaqWgILSxYFCoumTf+on8BRq/zQRNnqthwunP/E+gEckF442rPDUN6/AtdeQSM/JUyiBqeOLicF4X6CQ9LnvKevFUTk1hxNmd9GXZmhR6FTxqaS+f6qFqsioQZJ36+UtNIkORZq6gfSQILanXu9SdHZcaybksZ5At8nzu/oDH3DnL2ztwLjQDRPbf4BDkm32m8sjtaI5mZfsCOa8itwSPrR7iGkg3jRhXV1OAST/gn9p7tDpB9AKBWfxA9ZSFVGCn0fPF/8NuBDyTUQEzOwGAK2d0yTMajA+T73npNXHUtQqj/5uB017KHM9aTVckN9tqTE0+HjFQ0sziJe8UOWctJ3s6iZ+aBbBL3cDNYAFKmfSRGnrZwDvXkeTdYbhbXp8WLT4/5uPgX3CaIBWw5qQ6MwNUUPs0Ap+mmurVJ2XtYBDAFlCsR7vFZgC84NPyNFOy5tpL94De2/XO6SvP5CEm6Y+rfK/lf5A5RpN2/mmB9oAAAAAElFTkSuQmCC"

app.geometry("450x300")
app.title("Trabajos diarios Stock")

label = ttk.Label(
    app,
    text="Comenzar con la selección",
    foreground="black",
    font=("Courier", 14),
)
label.place(x=70, y=50)

combo = ttk.Combobox(
    app,
    values=["Javi", "Yohan"],
    state="readonly",
    justify="center",
)
combo.place(x=250, y=50)

button = ttk.Button(
    app,
    text="Zooplus",
    command=partial(zooplus, combo)
)
button.place(x=50, y=100)

button2 = ttk.Button(
    app,
    text="Nike",
    command=partial(nike, combo)
)
button2.place(x=250, y=100)

button3 = ttk.Button(
    app,
    text="Electrolux",
    command=partial(electrolux, combo)
)
button3.place(x=50, y=150)

button5 = ttk.Button(
    app,
    text="Stock Operaciones",
    command=partial(operaciones, combo)
)
button5.place(x=250, y=150)

image = tk.PhotoImage(data=b64decode(raw_image))
label2 = ttk.Label(
    image=image
)
label2.place(x=275, y=190)

button4 = ttk.Button(
    app,
    text="Salir",
    command=app.destroy
)
button4.place(x=250, y=250)

app.mainloop()
