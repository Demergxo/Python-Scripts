import tkinter as tk

root = tk.Tk()
root.geometry("300x200")

# Crear un widget de ejemplo
label = tk.Label(root, text="Sticky Example", bg="lightblue", width=20, height=10)
label.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

# Configurar las filas y columnas para que se expandan
root.grid_rowconfigure(0, weight=1)
root.grid_columnconfigure(0, weight=1)

root.mainloop()
