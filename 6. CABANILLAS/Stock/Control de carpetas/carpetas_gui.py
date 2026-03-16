#Author: Javier García-Merás Palacios
#version : 0.1
#Description: Aplicación para el borrado masivo de carpetas vacias y creacion de carpetas de meses o dias


from tkinter import Image, Listbox, filedialog, font, messagebox, ttk, StringVar, TOP
import os
from functools import partial
from base64 import b64decode
import tempfile
import datetime as dt

from PIL import Image, ImageTk
import tkinter as tk

raw_image = "iVBORw0KGgoAAAANSUhEUgAAAHwAAAAuCAMAAADdho1wAAAAV1BMVEVHcEz/OgD/OgD/OgD/OgD/OgD/OgD/OgD/OgD/OgD/OgD/OgD/OgD/OgD/OgD/OgD/OgD/OgD/OgD/OgD/OgD/OgD/OgD/OgD/OgD/OgD/OgD/OgD/OgD/maxbAAAAHHRSTlMAOZ4DJi3nBvftGwy7zNVo3RNcRk20w4eoe5JvWvIB4QAAA/5JREFUWMPNWNuypCoMbS94Q1QUUdT//85x79Y2IRG7ps6pmlQ/AWZ1FrmR1+tfk0RqrWX+H2nL5dfKdNQuo1VK2TF2pkqunUpckiJleQq2JNa2vrXVsRuqB5OjSZXbJUU3959Phq78SNbDr/rs2rEV0lYAZU08yHvsKIbIhzTuUJfHYFUBM9IGIPQhbUVtbvjXEwP9I6OkINt0GQj/VHwq1y7jdBVxyppteeitWM8jPSCxjM5VA1abU7UYb7RtzUCxTXd3ev5cFCL+5KNSDOlRs91K2RPs7O5sJ25ut32vTQzpUbdt36Pfnz4xKPHdL8VRSUlPmy0oJWK+stsz6YT4ZU8CcqSky3F7kAZ4XbL45pZZVhDSf06mgKLCvF4rQ7rzte3iLcVXxA0oxgrlBpGKqI87GLaHtECP1aKj5ogMh7YzUWRcjfB//vfB5YwcrNVvI/fbcBNJSRIedjHj6YhGaw4N0lgudyCf2SziOaExCY2FdJ5MIsNjkAgr+LeLgfmrSjyWnrYI+hC88VmjFArR42OtuQsCXhDxhHRpeaf2Q7B5czJA7pIvqr1gksLHfQW4w9X/dCW8r1zCDsoaCNweuC4p4BUw3f2uAI+10LmHtb1kNYATkkVARE7kWqEs3m5ec3VyjwGc7ev8fg/mDGBKyzirp1Aq9rhvHQJ/rcVNtsxHGk3wX1/fKek5O8hnfo7E4FrBvQUk/4vHgnEg4I6N9sDNLbEeuEEJuRFfgic+OEu7rrcQeKW80pdztJtn2lmHc1sInFbB677mQJijQHwrBP455lyZI+CGJNguZUJtTh5DDVqZvS8vd/X4lowD90lHwQZsy9JQklmJHe64uVNiBpyQjoiH6XUKhPkRiFXHd4v4Si5wUwaqWgILSxYFCoumTf+on8BRq/zQRNnqthwunP/E+gEckF442rPDUN6/AtdeQSM/JUyiBqeOLicF4X6CQ9LnvKevFUTk1hxNmd9GXZmhR6FTxqaS+f6qFqsioQZJ36+UtNIkORZq6gfSQILanXu9SdHZcaybksZ5At8nzu/oDH3DnL2ztwLjQDRPbf4BDkm32m8sjtaI5mZfsCOa8itwSPrR7iGkg3jRhXV1OAST/gn9p7tDpB9AKBWfxA9ZSFVGCn0fPF/8NuBDyTUQEzOwGAK2d0yTMajA+T73npNXHUtQqj/5uB017KHM9aTVckN9tqTE0+HjFQ0sziJe8UOWctJ3s6iZ+aBbBL3cDNYAFKmfSRGnrZwDvXkeTdYbhbXp8WLT4/5uPgX3CaIBWw5qQ6MwNUUPs0Ap+mmurVJ2XtYBDAFlCsR7vFZgC84NPyNFOy5tpL94De2/XO6SvP5CEm6Y+rfK/lf5A5RpN2/mmB9oAAAAAElFTkSuQmCC"




def borrado_carpetas(ruta):
    dir_path = ruta.get()
    
    if not os.path.exists(dir_path):
        messagebox.showerror("Sistema", f"El directorio no existe: {dir_path}")
    else:
        for root, dirs, files in os.walk(dir_path, topdown=False):
            for dir_name in dirs:
                carpeta = os.path.join(root, dir_name)
                if len(os.listdir(carpeta)) == 0:
                    try:
                        os.rmdir(carpeta)
                    except OSError as e:
                        messagebox.showerror("Sistema", f"Error al eliminar la carpeta: {e}")
        messagebox.showinfo("Sistema", f"Carpetas eliminadas en: {dir_path}")

def crear_carpetas_mes(ruta):
    
    dir_path=ruta.get()
    
    meses = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]

    try: 
        num = 1
        os.makedirs(dir_path, exist_ok=True)
        for mes in meses:
            path_full = os.path.join(dir_path, f"{str(num).zfill(2)}. {mes}")
            num = num + 1
            os.makedirs(path_full, exist_ok=True)
        messagebox.showinfo("Sistema", f"Carpetas creadas en: {dir_path}")    
    except KeyboardInterrupt:
        messagebox.showerror("Sistema", "Saliendo del programa...")

def crear_carpetas_dia(path, anno, mes):
    ruta = path.get()
    year = int(anno.get())
    month = int(mes.get())
    # Obtener el número de días en el mes y año dados
    num_dias = obtener_dias_en_mes(year, month)
    
    # Crear las carpetas
    for dia in range(1, num_dias + 1):
        fecha = dt.datetime(year, month, dia)
        formato_fecha = fecha.strftime("%Y-%m-%d")
        nueva_ruta = os.path.join(ruta, formato_fecha)
        
        # Crear la carpeta si no existe
        if not os.path.exists(nueva_ruta):
            os.makedirs(nueva_ruta)
        else:
            messagebox.showerror("Sistema", f"Carpeta ya existe: {nueva_ruta}")
    messagebox.showinfo("Sistema", f"Carpetas creadas en: {ruta}")         

def obtener_dias_en_mes(year, month):
    # Calcula el número de días en el mes y año dados
    if month == 12:
        next_month = 1
        next_year = year + 1
    else:
        next_month = month + 1
        next_year = year
    
    # Primer día del próximo mes
    primer_dia_siguiente_mes = dt.datetime(next_year, next_month, 1)
    
    # Último día del mes actual
    ultimo_dia_mes_actual = primer_dia_siguiente_mes - dt.timedelta(days=1)
    
    return ultimo_dia_mes_actual.day

def borrado_masivo():
    app2 =tk.Toplevel(app)
    app2.title("Borrado de Carpetas")
    app2.geometry("400x270")
    app2.resizable(width=False, height=False)
    
    icon_borrado = "AAABAAEAEBAAAAEAIABoBAAAFgAAACgAAAAQAAAAIAAAAAEAIAAAAAAAAAQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAWAAAAFgAAABYAAAAWAAAAFgAAABYAAAAWAAAAFgAAABYAAAAWAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACbAAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAJIAAAAAAAAAAAAAAAAAAAAAAAAAtwAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAACuAAAAAAAAAAAAAAAAAAAAAAAAANMAAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAAygAAAAAAAAAAAAAAAAAAAAAAAADvAAAA/wAAAP8AAAD/AAAA+gAAAP8AAAD/AAAA+wAAAP8AAAD/AAAA/wAAAOYAAAAAAAAAAAAAAAAAAAAAAAAA/wAAAP8AAAD/AAAA/wAAAHgAAABUAAAATQAAAH8AAAD/AAAA/wAAAP8AAAD+AAAAAAAAAAAAAAAAAAAAAAAAAP8AAAD/AAAA/wAAAP8AAAD/AAAAFwAAABsAAAD/AAAA/wAAAP8AAAD/AAAA/wAAAAAAAAAAAAAAAAAAAAAAAAD/AAAA/wAAAP8AAAD/AAAA+wAAAAAAAAAAAAAA/QAAAP8AAAD/AAAA/wAAAP8AAAAAAAAAAAAAAAAAAAAAAAAA/wAAAP8AAAD/AAAA/wAAAEEAAADxAAAA7QAAAEoAAAD/AAAA/wAAAP8AAAD/AAAAAAAAAAAAAAAAAAAAAAAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAAAAAAAAAAAAAAAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAAAAAAABUAAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAA0AAABXAAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAABPAAAAOQAAAJUAAACVAAAAlQAAAMsAAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAACVAAAAlQAAAJUAAACVAAAAMwAAAAAAAAAAAAAAAAAAAAAAAACAAAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACcAAAAnAAAAJwAAACcAAAAnAAAAEwAAAAAAAAAAAAAAAAAAAAAAAAAA4AcAAMADAADAAwAAwAMAAMADAADAAwAAwAMAAMGDAADAAwAAwAMAAIABAAAAAAAAAAAAAAAAAADwHwAA+B8AAA=="

    icon_path2 = os.path.join(tempfile.gettempdir(), "app2_icon.ico")
    with open(icon_path2, "wb") as icon2_file:
        icon2_file.write(b64decode(icon_borrado))
        
    app2.iconbitmap(icon_path2)
    
    #entry_text = StringVar()
    
    
    label2 = ttk.Label(
        app2,
        text="Ingrese ruta:",
        foreground="black",
        font=("Helvetica", 20, "bold"),
    )
    label2.place(x=105, y=37)
    
    ruta = tk.Entry(
        app2,
        width=40, 
        font=font.Font(family="Times", size=12),
        justify=tk.CENTER,
        #textvariable=entry_text
        )
    ruta.place(x=20, y=80)
    #entry_text.set(r"Ej: C:\Users\[usuario]\GXO\SPCABANILLAS - Cabanillas_Zooplus")
    
    button_borrado = tk.Button(
        app2,
        text = "Borrado",
        command=partial(borrado_carpetas, ruta),
        width=18
    )
    button_borrado.place(x=25, y=135)
    
    button_salir = tk.Button(
        app2,
        text= "Salir",
        fg="red",
        command=app2.destroy,
        width=18
    )
    button_salir.place(x=230, y=135)
    
    button_borrar = tk.Button(
        app2,
        text="Limpiar Texto",
        
        width=18
    )
    button_borrar.place(x=25, y=180)
    button_borrar.config(command=lambda: ruta.delete(0, tk.END))
    
    cab_img = "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"
    
    image = tk.PhotoImage(data=b64decode(cab_img))
    label2 = ttk.Label(
        app2,
        image=image,
               
    )
    label2.place(x=265, y=175)
    
    app2.mainloop()
    
def crear_carpetas_por_mes():
    app3 = tk.Toplevel(app)
    app3.title("Crear carpetas por mes")
    app3.geometry("400x270")
    app3.resizable(height=False, width=False)
    
    icon_crear_carpeta = "AAABAAEAEBAAAAEAIABoBAAAFgAAACgAAAAQAAAAIAAAAAEAIAAAAAAAAAQAANcNAADXDQAAAAAAAAAAAAAAAACAAAAA5gAAAPIAAADxAAAA8QAAAPEAAADxAAAA8QAAAPEAAADxAAAA8QAAAPEAAADxAAAA8gAAAOYAAACAAAAA5gAAAJIAAABNAAAATgAAAE4AAABOAAAATAAAAEwAAABOAAAATgAAAE4AAABOAAAATgAAAE0AAACSAAAA5gAAAPEAAABOAAAAAAAAAAAAAAAAAAAAAAAAACMAAAAzAAAAAQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAATgAAAPEAAADxAAAATgAAAAAAAAAAAAAAAAAAAC0AAAC6AAAA0QAAAD8AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAE4AAADxAAAA8QAAAE4AAAAAAAAAAAAAADQAAAC9AAAAuAAAALAAAADDAAAAMQAAAAAAAAAAAAAAAAAAAAAAAABOAAAA8QAAAPEAAABOAAAAAAAAAAsAAACaAAAArgAAACMAAAAeAAAAsAAAALgAAAAlAAAAAAAAAAAAAAAAAAAATgAAAPEAAADxAAAATgAAAAAAAAACAAAALwAAAB4AAAAAAAAAAAAAACoAAAC+AAAAqQAAABsAAAAAAAAAAAAAAE4AAADxAAAA8QAAAE4AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAANwAAAMkAAACQAAAACgAAAAAAAABOAAAA8QAAAPEAAABNAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABBAAAAYgAAAAcAAAAAAAAATQAAAPEAAADyAAAAXQAAABMAAAAWAAAAFgAAABYAAAAWAAAAFgAAABYAAAAWAAAAFgAAABcAAAAWAAAAEwAAAF0AAADyAAAA+wAAANMAAAC/AAAAvwAAAMAAAADAAAAAwAAAAMAAAADAAAAAwAAAAMAAAADAAAAAvwAAAL8AAADTAAAA+wAAAPYAAACVAAAAagAAAHAAAABoAAAAZwAAAGcAAABnAAAAZwAAAGcAAABnAAAAaAAAAHAAAABqAAAAlQAAAPYAAADyAAAATgAAAEIAAACDAAAADgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA4AAACDAAAAQgAAAE4AAADyAAAA1wAAALQAAAC0AAAA4QAAAI0AAACBAAAAggAAAIIAAACCAAAAggAAAIEAAACNAAAA4QAAALQAAAC0AAAA1wAAAEgAAACcAAAA0AAAAOsAAAC2AAAArgAAAK8AAACvAAAArwAAAK8AAACuAAAAtgAAAOsAAADQAAAAnAAAAEgAAAAAAAAABgAAAG8AAADDAAAAIgAAAAsAAAAMAAAADAAAAAwAAAAMAAAACwAAACIAAADDAAAAbwAAAAYAAAAAAAAAAAAAAAA8fAAAOHwAADA8AAAgHAAAIwwAAD+EAAA/xAAAAAAAAAAAAAAAAAAAB+AAAAAAAAAAAAAAgAEAAA=="

    icon_path2 = os.path.join(tempfile.gettempdir(), "app3_icon.ico")
    with open(icon_path2, "wb") as icon2_file:
        icon2_file.write(b64decode(icon_crear_carpeta))
        
    app3.iconbitmap(icon_path2)
    
    label2 = ttk.Label(
        app3,
        text="Ingrese ruta:",
        foreground="black",
        font=("Helvetica", 20, "bold"),
    )
    label2.place(x=105, y=37)
    
    ruta = tk.Entry(
        app3,
        width=40, 
        font=font.Font(family="Times", size=12),
        justify=tk.CENTER,
        )
    ruta.place(x=20, y=80)
    
    button_crear_carpeta = tk.Button(
        app3,
        text = "Crear",
        command=partial(crear_carpetas_mes, ruta),
        width=18
    )
    button_crear_carpeta.place(x=25, y=135)
    
    button_salir = tk.Button(
        app3,
        text= "Salir",
        fg="red",
        command=app3.destroy,
        width=18
    )
    button_salir.place(x=230, y=135)
    
    button_borrar = tk.Button(
        app3,
        text="Limpiar Texto",
        
        width=18
    )
    button_borrar.place(x=25, y=180)
    button_borrar.config(command=lambda: ruta.delete(0, tk.END))
    
    cab_img = "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"
    
    image = tk.PhotoImage(data=b64decode(cab_img))
    label2 = ttk.Label(
        app3,
        image=image,
               
    )
    label2.place(x=265, y=175)
    
    app3.mainloop()

def crear_carpetas_por_dia():
    def limpiar_texto():
        ruta.delete(0, tk.END)
        mes.delete(0, tk.END)
        anno.delete(0, tk.END)
    
    app4 = tk.Toplevel(app)
    app4.title("Crear carpetas por mes")
    app4.geometry("400x400")
    app4.resizable(height=False, width=False)
    
    icon_crear_carpeta_dia = "AAABAAEAEBAAAAEACABoBQAAFgAAACgAAAAQAAAAIAAAAAEACAAAAAAAAAEAANcNAADXDQAAAAEAAAABAAD5pgAA8pQAAPmmAAD4pgAA/6MAAG+0jAAEu/kAFbHoAP+fAADqqBEACLz0AAi19QDjmhYA+p4AAPObAADzmgAA+aYAAPmmAAD4pgAA+6UAANynHQAvs80AfZ56AP2hAAD0pAQATbKtAEukrgDvlwUA85oAAPKYAADxlgAA8JQAAPmlAAD5pgAA75IAAO+RAAD5pgAA+aUAAO2MAADsiwAA+KUAAPikAADqhwAA6oYAAPaiAAD2oQAA6IIAAOeAAADznAAA85sAAOZ8AADlewAA8pcAAPGTAADkeAAA5HgAAPeiAADzkwAA534AAOd9AAD4pgAA96MAAOd+AADmfQAA+KUAAPejAADmfQAA5nsAAPekAAD2ogAA5XsAAOV6AAD3owAA5HgAAPOaAQDnlAoA23cKAON2AQDZjyoArJVuALCffgCvnn0ArJp5AKqZeACpmHcAqJd2AKiWdgCnlXUAppR0AKaTcwCoj2oAz3smALm8swC3uKwAtLWoALe4qgC2t6kAtLanALK0pQCxsqMAsLGiAK6voACsrp4Aq6ydAKqrmwCoqZkAp6mYAKWpmgD5pgAA+aUAAPCmCACZpl8AxpkuAPigAAD1oQAAraNJAKmWSgDxlQAA8ZcAAPCUAAD4pQAA96QAAPWfAAD0nAAA85oAAPKXAADwkwAA75EAAO2PAAD2ogAA9qwmAPe+WQD1tkoA8ZsQAPCUAwDyqDQA75kZAOyLAADriQAA85wAAPSnIgD53KkA99CRAPnZqQD1xHgA8q5JAPrmxwDwqkoA6oQAAOmEAADymQAA9LNKAPjYpwDulQ8A8axGAPfYqwDwqEYA+Ny2AO+oTgDnfwAA5n4AAPCRAADujgAA8rFPAPbRnQDsjQcA76I5APbVqADrkR4A9M2bAO2mTwDlewAA5XoAAO+FAADugwAA8apNAPTOmgDujAcA8KI4APTTpQDulR4A882ZAO6pTQDogQAA54AAAPOUAADvhgAA86pKAPjWpwDwkQ8A8qpGAPjXqgDvlxwA8KxPAOmCAADylAAA8psiAPnYqgD3zJAA+NeoAPXCeQDtkQ4A9s6WAO+pSwD0mwAA8ZQAAPKgKAD0tlsA869MAO6TEADsiwIA7p0vAOuPFwDnfgAA9qEAAPWeAADxkgAA8I4AAO+MAADtiwAA7IkAAOuFAADogAAA530AAOOSDwDkkhAA448QAOGMDgDfiQ4A3ocOAN6FDgDdgw4A3IAOANp+DgDafA4A2HoOAKiYdwClknMA////AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAXF1eX2BhYmNkZWZnaGlqa05P7FBRUlNUVVZXWFntWltKS+Dh4uPk5ebn6Onq60xNSNbXzH3Y2drb3N3C3t+sSURFeszNzs/Q0dLT1LfVRkdAQXrDxMXGx8jJysu3uEJDPD25uru8vb6/wKTBwrc+Pzg5ra6vsLGys7S1tre4Ojs0NaGio6SlpqeoqaqrrDY3MDGWdZeYmZqbnJ2en6AyMywteouMjY6PkJGSk5SVLi8oKXmBeoKDhIWGh4iJiiorJCV4eHl6e3t8fX5+f4AmJyAhbG1ub3BxcnN0dXZ3IiMQERITFBUWFxgZGhscHR4fAAIDBAUGBwgJCgsMDQ4PAQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAIABAAA="

    icon_path2 = os.path.join(tempfile.gettempdir(), "app4_icon.ico")
    with open(icon_path2, "wb") as icon2_file:
        icon2_file.write(b64decode(icon_crear_carpeta_dia))
        
    app4.iconbitmap(icon_path2)
    
    label2 = ttk.Label(
        app4,
        text="Ingrese ruta:",
        foreground="black",
        font=("Helvetica", 20, "bold"),
    )
    label2.place(x=105, y=20)
    
    ruta = tk.Entry(
        app4,
        width=40, 
        font=font.Font(family="Times", size=12),
        justify=tk.CENTER,
        )
    ruta.place(x=20, y=57)
    
    label3 = ttk.Label(
        app4,
        text="Ingrese año (Ej: 2024):",
        foreground="black",
        font=("Helvetica", 20, "bold"),
    )
    label3.place(x=55, y=100)
    
    anno = tk.Entry(
        app4,
        width=40, 
        font=font.Font(family="Times", size=12),
        justify=tk.CENTER,
        )
    anno.place(x=20, y=137)
    
    label4 = ttk.Label(
        app4,
        text="Ingrese mes en numero (Ej: 7 para julio):",
        foreground="black",
        font=("Helvetica", 14, "bold"),
    )
    label4.place(x=15, y=180)
    
    mes = tk.Entry(
        app4,
        width=40, 
        font=font.Font(family="Times", size=12),
        justify=tk.CENTER,
        )
    mes.place(x=20, y=217)
    
    button_crear_carpeta = tk.Button(
        app4,
        text = "Crear",
        command=partial(crear_carpetas_dia, ruta, anno, mes),
        width=18
    )
    button_crear_carpeta.place(x=25, y=275)
    
    button_salir = tk.Button(
        app4,
        text= "Salir",
        fg="red",
        command=app4.destroy,
        width=18
    )
    button_salir.place(x=230, y=275)
    
    button_borrar = tk.Button(
        app4,
        text="Limpiar Texto",
        width=18,
        command=limpiar_texto,
    )
    button_borrar.place(x=25, y=315)
    
    cab_img = "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"
    
    image = tk.PhotoImage(data=b64decode(cab_img))
    label6 = ttk.Label(
        app4,
        image=image,
               
    )
    label6.place(x=265, y=315)
 
    
    app4.mainloop()

app = tk.Tk()

icon_main ="AAABAAEAEBAAAAEACABoBQAAFgAAACgAAAAQAAAAIAAAAAEACAAAAAAAAAEAAMMOAADDDgAAAAEAAAABAAAAAAAAL9u6ABGwWAD44HQA+d+HANyoTQDZp0YAALD8ACrbuwA027kADrNdABKvVgD/4GgArt6NAGvcpQBCoUYASKJIAE/WowBPyo4AUcmLAE3JkQD74W8A9+BzAO3fdQBbsWwAQ8GWAD3GpQBAxaEAQ8OdAE3CkAAm2P8Ag9zCAKrdpwBOvYwAK9j+AC3Y/AAt1/sAVbl/ACvY/wBerWoAKdf/AGihVwAm1f8Aa6FWACPT/gBuoVQAINL9AHCgUQAe0PwAdZpHABvP/ACqmj4AeokyABjN/AC7tXEAx6FDAHJ1HwAWy/wAGbzoALCydQDoslEAEcT8AAe49QBesaoA/50AAAq0/AAIsf0AAKv8AACs/AAAsv0ANdy5ADXbuAA02rUAH8+aABDCfABm3KYAZ9qjAGbUnQBkzZQAVMB0ADm1XwDr3HQA6tpxAOfQZgDes0QA354eALWZIQCp26UAp9ikAJ7RogCYxJsAnaJ2AMWVMAC/lB8AdLBpAES6rwA7uL0ANLe/AC63ugAr1vsAKNT6ABjG+QAHrvgAEofyAHKLiwDatUwA3chxANPHfQDPxYAAur95AGy2fgAp1/8AJtb/ACPT/gAh0v4AFsX9AAiq/AAdg/YAUoaqAJuxeAC72MAAwNnBANzWqgDsx3UAmq5YACfW/wAk0/4AIdL9AB7Q/QAbzv0AF8n9ABjE/AApsvQANaftADer9QA1q/YAVrrHAM62WwCfqlEAJNT+ABzP/QAZzf4AFsz+ABPL/gAnrPwANJP5ADKS+AAukvoAJLHiAKqoXQCcpk0AE8r+ABHI/QAPxf0ADMP8AArB+wAFwP0AG7zlAKinYQCZokwAEcj+AA7H/QALxf0ACcT8AAbC/AABwP4AGrznAK+saACdpE0ADMX9AAbB/AADwP0AAL/+ABu85wC0sG0Ao6NKABnN/QABvvwAAL7+ABu86AC4s28AFsz9AAG+/QAAvvwAHL3oABPK/QABv/0AAL79AA/D/QAMwf0ACr/9AAi+/AAFvfwAA7v8AAG6/AAAufwABrD9AASu/QADrv0AAa39AACs/QAAq/0A////AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAQULExcbHyMnJyclDREUHAD28vb6/wMHCw8PDwz4/QAY5uaChqaOkq7q7u7I6OzwFNbWXoKGpo6qrtreyuDY3ODKwjpegoamjqquxsrO0MzQwjI2Ol6ChqaOqq6ytrq8xLoCMjY6XoKGio6SlpqeoLyxygIyNjpeYmZqbnJ2eny0qi3+AjI2Oj5CRkpOUlZYrKH1+f4CBgoOEhYaHiImKKSZvcHFyc3R1dnd4eXp7fCciIyRjZGVmZ2hpamtsbW4lHh8gV1hZWltcXV5fYGFiIQQVFhdRUlNUVVYYGRobHB0DDA0OS0xNTk9QDxAREhMUAAEICUZGR0hJSgoLAgAAAAADAAAAAQAAAAEAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACAAAAAgAAAAMAPAAA="

icon_path = os.path.join(tempfile.gettempdir(), "app_icon.ico")
with open(icon_path, "wb") as icon_file:
    icon_file.write(b64decode(icon_main))

app.geometry("450x300")
app.title("Gestión de Carpetas")
app.resizable(width=False, height=False)

app.iconbitmap(icon_path)

label = ttk.Label(
    app,
    text="Gestión de Carpetas",
    foreground="black",
    font=("Helvetica", 20, "bold"),
)
label.place(x=60, y=40)

button_borrar = tk.Button(
    app,
    text="Borrado Masivo",
    command=borrado_masivo,
    width=16
   
)
button_borrar.place(x=50, y=100)

button_crear_mes = tk.Button(
    app,
    text="Creación por mes",
    command=crear_carpetas_por_mes,
    width=16
   
)
button_crear_mes.place(x=50, y=140)

button_crear_dia = tk.Button(
    app,
    text="Creación por día",
    command=crear_carpetas_por_dia,
    width=16
    
)
button_crear_dia.place(x=250, y=100)

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
