import tkinter as tk

app = tk.Tk()
palabra = tk.StringVar(app)
entrada = tk.StringVar(app)




#definimos dimensiones : ancho x alto
app.geometry("600x300")

#cambiamos color de fondo
app.configure(background="black")

#cambiamos tirulo de ventana
tk.Wm.wm_title(app, "Generador CSV Turnos")

def saludar():
    print("Hola " + entrada.get())
    
def cambiar_palabra():
    palabra.set("Sus" + entrada.get())

tk.Label(
    app,
    text="Etiqueta",
    textvariable=palabra,
    foreground="white",
    bg="black",
    justify="center",
    
).pack(
    fill=tk.BOTH,
    expand=True,
)

tk.Button(
    app,
    text="Click!",
    font=("Courier", 14),
    bg="#00a8e8",
    foreground="white",
    command=cambiar_palabra,
    relief="flat",
    
      
).pack(
    fill=tk.BOTH,
    expand=True,
)

tk.Entry(
    app,
    foreground="white",
    bg="black",
    justify="center",
    textvariable=entrada,
    
    
).pack(
    fill=tk.BOTH,
    expand=True,
)


app.mainloop()

