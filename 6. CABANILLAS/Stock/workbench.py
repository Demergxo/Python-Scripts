import tkinter as tk
from tkinter import Listbox, filedialog, messagebox, ttk
from tkinterdnd2 import DND_FILES, TkinterDnD
import os
from functools import partial
from base64 import b64decode
import tempfile
import shutil

# # Icono en formato base64 (debes reemplazar "[cadena base64]" con tu base64 real)
# icon_main = "[cadena base64]"

# # Decodificar la cadena base64 del icono
# icon_path = os.path.join(tempfile.gettempdir(), "app_icon.ico")
# with open(icon_path, "wb") as icon_file:
#     icon_file.write(b64decode(icon_main))

# Función para abrir archivos o carpetas
def abrir_archivo_o_carpeta(ruta):
    if os.path.isdir(ruta):
        listar_archivos(ruta)
    else:
        os.startfile(ruta)

# Función para listar archivos y carpetas en el Listbox
def listar_archivos(ruta):
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
    listbox_archivos.current_path = ruta

# Función para manejar la selección de usuario
def indicadores(combo_value):
    try:
        if combo_value == "Javi":
            ruta = r"C:\Users\jgmeras\GXO\SPCABANILLAS - Cabanillas_Zooplus\6. Stock\05. Indicadores Zooplus"
        elif combo_value == "Yohan":
            ruta = r"C:\Users\yrodriguez\GXO\SPCABANILLAS - Cabanillas_Zooplus\6. Stock\05. Indicadores Zooplus"
        listar_archivos(ruta)
    except:
        messagebox.showinfo("Sistema", "Archivo no encontrado")

# Función para manejar el doble clic en el Listbox
def on_double_click(event):
    seleccion = listbox_archivos.curselection()
    if seleccion:
        archivo = listbox_archivos.get(seleccion)
        ruta_completa = os.path.join(listbox_archivos.current_path, archivo)
        abrir_archivo_o_carpeta(ruta_completa)

# Función para manejar el evento de arrastrar y soltar
def on_drop(event):
    archivos_arrastrados = event.data.split()
    for archivo in archivos_arrastrados:
        if os.path.isfile(archivo):
            destino = os.path.join(listbox_archivos.current_path, os.path.basename(archivo))
            shutil.move(archivo, destino)
            listar_archivos(listbox_archivos.current_path)

# Crear la ventana principal
app = tk.Tk()
app.geometry("450x300")
app.title("Trabajos diarios Stock")
#app.iconbitmap(icon_path)



label = ttk.Label(
    app,
    text="Seleccione usuario",
    foreground="black",
    font=("Courier", 12),
)
label.place(x=50, y=40)

combo = ttk.Combobox(
    app,
    values=["Javi", "Yohan"],
    state="readonly",
    justify="center",
)
combo.place(x=250, y=40)

# Crear la ventana secundaria para Zooplus
def zooplus(combo):
    combo_value = combo.get()
    app2 = tk.Toplevel(app)
    app2.title("Zooplus")
    app2.geometry("400x600")
        
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
    
    global listbox_archivos
    listbox_archivos = Listbox(
        app2,
        width=50,
        height=20
    )
    listbox_archivos.place(x=50, y=100)
    listbox_archivos.current_path = ""
    listbox_archivos.bind("<Double-1>", on_double_click)
    listbox_archivos.drop_target_register(DND_FILES)
    listbox_archivos.dnd_bind('<<Drop>>', on_drop)
    
    button11 = ttk.Button(
        app2,
        text="Salir",
        command=app2.destroy    
    )
    button11.place(x=250, y=540)
    app2.mainloop()

button = ttk.Button(
    app,
    text="Zooplus",
    command=partial(zooplus, combo)
)
button.place(x=50, y=100)

button4 = ttk.Button(
    app,
    text="Salir",
    command=app.destroy
)
button4.place(x=310, y=250)

app.mainloop()

# Borrar el archivo temporal del icono
#os.remove(icon_path)
