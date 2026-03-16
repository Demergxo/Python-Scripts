import tkinter as tk
from tkinter import filedialog, messagebox
import os

# Función para seleccionar la carpeta
def seleccionar_carpeta():
    carpeta = filedialog.askdirectory()
    if carpeta:
        carpeta_var.set(carpeta)
        abrir_ventana_archivos(carpeta)

# Función para abrir la ventana secundaria y listar archivos
def abrir_ventana_archivos(carpeta):
    ventana_archivos = tk.Toplevel()
    ventana_archivos.title("Archivos en " + carpeta)

    listbox_archivos = tk.Listbox(ventana_archivos, width=50, height=15)
    listbox_archivos.pack(padx=10, pady=10)

    archivos = os.listdir(carpeta)
    for archivo in archivos:
        listbox_archivos.insert(tk.END, archivo)

    boton_abrir = tk.Button(ventana_archivos, text="Abrir Archivo", command=lambda: abrir_archivo(carpeta, listbox_archivos.get(tk.ACTIVE)))
    boton_abrir.pack(pady=10)

# Función para abrir el archivo seleccionado
def abrir_archivo(carpeta, archivo_seleccionado):
    ruta_archivo = os.path.join(carpeta, archivo_seleccionado)
    try:
        with open(ruta_archivo, 'r') as file:
            contenido = file.read()
            messagebox.showinfo("Contenido del archivo", contenido)
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo abrir el archivo: {e}")

# Crear la ventana principal
ventana = tk.Tk()
ventana.title("Selector de Archivos")

# Variable para almacenar la ruta de la carpeta
carpeta_var = tk.StringVar()

# Crear los widgets
label_carpeta = tk.Label(ventana, text="Carpeta:")
entry_carpeta = tk.Entry(ventana, textvariable=carpeta_var, width=50)
boton_seleccionar = tk.Button(ventana, text="Seleccionar Carpeta", command=seleccionar_carpeta)

# Colocar los widgets en la ventana
label_carpeta.grid(row=0, column=0, padx=10, pady=10)
entry_carpeta.grid(row=0, column=1, padx=10, pady=10)
boton_seleccionar.grid(row=0, column=2, padx=10, pady=10)

# Iniciar el bucle principal de la interfaz
ventana.mainloop()
