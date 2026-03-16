import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from functools import partial
from ctypes import windll, wintypes, byref
from PIL import Image, ImageTk

# Función para obtener icono de archivo o carpeta
def obtener_icono(path):
    SHGFI_ICON = 0x000000100
    SHGFI_SMALLICON = 0x000000001

    shinfo = wintypes.SHFILEINFO()
    windll.shell32.SHGetFileInfoW(path, 0, byref(shinfo), wintypes.sizeof(shinfo), SHGFI_ICON | SHGFI_SMALLICON)
    hicon = shinfo.hIcon

    icon_info = wintypes.ICONINFO()
    windll.user32.GetIconInfo(hicon, byref(icon_info))
    bmp = wintypes.BITMAP()
    windll.gdi32.GetObjectW(icon_info.hbmColor, wintypes.sizeof(bmp), byref(bmp))

    pil_image = Image.frombuffer('RGBA', (bmp.bmWidth, bmp.bmHeight), icon_info.hbmColor, 'raw', 'BGRA', 0, 1)
    return ImageTk.PhotoImage(pil_image)

# Listar archivos y carpetas con iconos
def listar_archivos_y_carpetas(carpeta, treeview_archivos):
    try:
        archivos = os.listdir(carpeta)
        treeview_archivos.delete(*treeview_archivos.get_children())
        for archivo in archivos:
            ruta = os.path.join(carpeta, archivo)
            icono = obtener_icono(ruta)
            if os.path.isdir(ruta):
                treeview_archivos.insert('', 'end', text=archivo, image=icono, values=[ruta])
                treeview_archivos.image_dict[archivo] = icono  # Guardar referencia al icono
            else:
                treeview_archivos.insert('', 'end', text=archivo, image=icono, values=[ruta])
                treeview_archivos.image_dict[archivo] = icono  # Guardar referencia al icono
    except Exception as e:
        messagebox.showinfo("Sistema", f"Error al listar archivos: {e}")

# Función para manejar los indicadores
def indicadores(combo_value, treeview_archivos, current_dir_var):
    try:
        if combo_value == "Javi":
            directorio = r"C:\Users\jgmeras\GXO\SPCABANILLAS - Cabanillas_Zooplus\6. Stock\05. Indicadores Zooplus"
        elif combo_value == "Yohan":
            directorio = r"C:\Users\yrodriguez\GXO\SPCABANILLAS - Cabanillas_Zooplus\6. Stock\05. Indicadores Zooplus"
        
        current_dir_var.set(directorio)
        listar_archivos_y_carpetas(directorio, treeview_archivos)
    except Exception as e:
        messagebox.showinfo("Sistema", f"Error: {e}")

# Función para abrir archivo o carpeta
def abrir_archivo_o_carpeta(current_dir_var, treeview_archivos):
    item_seleccionado = treeview_archivos.selection()[0]
    ruta_seleccionada = treeview_archivos.item(item_seleccionado, 'values')[0]
    try:
        if os.path.isdir(ruta_seleccionada):
            current_dir_var.set(ruta_seleccionada)
            listar_archivos_y_carpetas(ruta_seleccionada, treeview_archivos)
        elif os.path.isfile(ruta_seleccionada):
            os.startfile(ruta_seleccionada)
        else:
            messagebox.showinfo("Sistema", "Selección no válida")
    except Exception as e:
        messagebox.showinfo("Sistema", f"No se pudo abrir: {e}")

# Función principal para la ventana Zooplus
def zooplus(combo):
    combo_value = combo.get()
    app2 = tk.Toplevel()
    app2.title("Zooplus")
    app2.geometry("600x600")

    current_dir_var = tk.StringVar()

    label = ttk.Label(
        app2,
        text="Tareas Disponibles",
        foreground="black",
        font=("Arial", 14)
    )
    label.place(x=75, y=10)

    treeview_archivos = ttk.Treeview(
        app2,
        columns=("fullpath"),
        displaycolumns=()
    )
    treeview_archivos.place(x=50, y=100, width=500, height=400)
    
    treeview_archivos.image_dict = {}  # Diccionario para mantener referencias a los iconos

    treeview_archivos.bind('<Double-1>', lambda event: abrir_archivo_o_carpeta(current_dir_var, treeview_archivos))

    button_indicadores = ttk.Button(
        app2,
        text="Indicadores",
        command=partial(indicadores, combo_value, treeview_archivos, current_dir_var)
    )
    button_indicadores.place(x=50, y=50)

    button_salir = ttk.Button(
        app2,
        text="Salir",
        command=app2.destroy
    )
    button_salir.place(x=250, y=540)

    app2.mainloop()

app = tk.Tk()

app.geometry("450x300")
app.title("Trabajos diarios Stock")

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

button_zooplus = ttk.Button(
    app,
    text="Zooplus",
    command=partial(zooplus, combo)
)
button_zooplus.place(x=50, y=100)

button_salir = ttk.Button(
    app,
    text="Salir",
    command=app.destroy
)
button_salir.place(x=310, y=250)

app.mainloop()
