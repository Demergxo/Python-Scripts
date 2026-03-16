import tkinter as tk
from tkinter import ttk
import pandas as pd

def export_to_excel(dataframe):
    # Exporta el DataFrame a un archivo Excel
    dataframe.to_excel("datos_modificados.xlsx", index=False)
    print("Archivo exportado: datos_modificados.xlsx")

def save_edits():
    for item in tree.get_children():
        values = tree.item(item, 'values')
        dataframe.loc[int(values[0]), editable_columns] = values[2:]  # type: ignore Ignora índice y columnas no editables
    export_to_excel(dataframe)

def delete_selected():
    selected_item = tree.selection()
    if not selected_item:
        print("No se ha seleccionado ninguna fila para eliminar.")
        return
    for item in selected_item:
        index = int(tree.item(item, 'values')[0])  # Obtiene el índice de la fila seleccionada
        dataframe.drop(index, inplace=True)  # Elimina del DataFrame
        tree.delete(item)  # Elimina del Treeview
    dataframe.reset_index(drop=True, inplace=True)  # Reinicia índices
    update_treeview()

def update_treeview():
    # Limpia el Treeview y lo actualiza con el DataFrame actual
    tree.delete(*tree.get_children())
    for idx, row in dataframe.iterrows():
        tree.insert("", "end", iid=idx, values=[idx] + list(row))# type: ignore

# Datos iniciales
data = {
    "Nombre": ["Producto A", "Producto B", "Producto C"],
    "Precio": [10, 20, 30],
}
dataframe = pd.DataFrame(data)
editable_columns = dataframe.columns  # Columnas editables

# Configuración de la ventana
root = tk.Tk()
root.title("Editor de DataFrame")

frame = ttk.Frame(root)
frame.pack(padx=10, pady=10)

# Define las columnas de la tabla, incluyendo un índice a la izquierda
columns = ["Índice"] + list(dataframe.columns)
tree = ttk.Treeview(frame, columns=columns, show="headings", height=5)

# Configura los encabezados de las columnas
for col in columns:
    tree.heading(col, text=col)
    tree.column(col, width=100)

# Inserta datos iniciales con el índice
for idx, row in dataframe.iterrows():
    tree.insert("", "end", iid=idx, values=[idx] + list(row))# type: ignore

tree.pack(side="left")

# Scroll vertical
scrollbar = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
tree.configure(yscrollcommand=scrollbar.set)
scrollbar.pack(side="right", fill="y")

# Edición en la tabla
def on_double_click(event):
    item_id = tree.focus()
    col_id = tree.identify_column(event.x)
    col_index = int(col_id[1:]) - 1
    if col_index > 0:  # La columna índice no es editable
        entry = ttk.Entry(root)
        entry.place(x=event.x_root - root.winfo_x(), y=event.y_root - root.winfo_y())
        entry.insert(0, tree.item(item_id, 'values')[col_index])
        entry.bind("<Return>", lambda e: save_entry(e, item_id, col_index, entry))
        entry.focus()

def save_entry(event, item_id, col_index, entry):
    new_value = entry.get()
    current_values = list(tree.item(item_id, 'values'))
    current_values[col_index] = new_value
    tree.item(item_id, values=current_values)
    entry.destroy()

tree.bind("<Double-1>", on_double_click)

# Botón para guardar y exportar
save_button = ttk.Button(root, text="Guardar y Exportar", command=save_edits)
save_button.pack(pady=5)

# Botón para eliminar fila seleccionada
delete_button = ttk.Button(root, text="Eliminar Selección", command=delete_selected)
delete_button.pack(pady=5)

root.mainloop()
