import tkinter as tk
from tkinter import filedialog, messagebox
import os
import win32com.client
import time

# Función para cargar los archivos del directorio en la Listbox
def cargar_directorio():
    dir_path = filedialog.askdirectory()
    if dir_path:
        listbox.delete(0, tk.END)  # Limpiar la Listbox
        archivos = [f for f in os.listdir(dir_path) if f.endswith(('.xlsx', '.xls'))]
        for archivo in archivos:
            listbox.insert(tk.END, os.path.join(dir_path, archivo))
        label_directorio.config(text=f"Directorio: {dir_path}")

# Función para refrescar los datos del archivo seleccionado (sin evento)
def refrescar_datos():
    seleccion = listbox.curselection()
    if not seleccion:
        messagebox.showwarning("Advertencia", "Por favor, selecciona un archivo de la lista.")
        return
    
    archivo_seleccionado = listbox.get(seleccion[0])
    try:
        # Leer el archivo Excel
        excel = win32com.client.Dispatch('Excel.Application')
        libro = excel.Workbooks.Open(archivo_seleccionado)
        # Refrescar los datos del libro
        libro.RefreshAll()
        excel.Visible = False  # Para evitar que la aplicación de Excel se muestre
        while True:
            estado = all(conexion.Refreshing == False for conexion in libro.Connections)
            if estado:
                break
            time.sleep(1)
        libro.Save()
        messagebox.showinfo("Sistema", "Libro actualizado")
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo leer el archivo: {e}")
    finally:
        libro.Close(SaveChanges=False)
        excel.Quit()

# Función para refrescar los datos del archivo seleccionado (con evento)
def refrescar_datos_event(event):
    refrescar_datos()

# Crear la ventana principal
root = tk.Tk()
root.title("Refrescar Datos de Excel")

# Crear el Frame principal
frame = tk.Frame(root)
frame.pack(pady=10)

# Crear el botón para seleccionar el directorio
btn_directorio = tk.Button(frame, text="Seleccionar Directorio", command=cargar_directorio)
btn_directorio.pack(pady=5)

# Crear un label para mostrar el directorio seleccionado
label_directorio = tk.Label(frame, text="Directorio: Ninguno")
label_directorio.pack(pady=5)

# Crear la Listbox
listbox = tk.Listbox(frame, selectmode=tk.SINGLE, width=50, height=10)
listbox.pack(pady=5)
listbox.bind('<Double-1>', refrescar_datos_event)  # Vincular el evento de doble clic

# Crear el botón para refrescar los datos
btn_refrescar = tk.Button(frame, text="Refrescar Datos", command=refrescar_datos)
btn_refrescar.pack(pady=5)

# Crear el Text widget para mostrar los datos
text_widget = tk.Text(frame, width=80, height=20)
text_widget.pack(pady=5)

# Ejecutar la aplicación
root.mainloop()
