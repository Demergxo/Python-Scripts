import tkinter as tk

# Función para actualizar la etiqueta desde la ventana secundaria
def actualizar_etiqueta():
    texto = entrada.get()
    etiqueta.config(text=texto)
    ventana_secundaria.destroy()

# Ventana principal
ventana_principal = tk.Tk()
ventana_principal.title("Ventana Principal")

# Crear una etiqueta en blanco
etiqueta = tk.Label(ventana_principal, text="")
etiqueta.pack(pady=20)

# Función para abrir la ventana secundaria
def abrir_ventana_secundaria():
    global entrada, ventana_secundaria
    ventana_secundaria = tk.Toplevel(ventana_principal)
    ventana_secundaria.title("Ventana Secundaria")
    
    # Crear un campo de entrada en la ventana secundaria
    entrada = tk.Entry(ventana_secundaria)
    entrada.pack(pady=10)
    
    # Botón para actualizar la etiqueta en la ventana principal
    boton_actualizar = tk.Button(ventana_secundaria, text="Actualizar", command=actualizar_etiqueta)
    boton_actualizar.pack()

# Botón para abrir la ventana secundaria
boton_abrir = tk.Button(ventana_principal, text="Abrir Ventana Secundaria", command=abrir_ventana_secundaria)
boton_abrir.pack(pady=10)

ventana_principal.mainloop()
