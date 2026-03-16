
#import re



def leer_archivo_implantaciones(path):
    import pandas as pd
    
    path = r"C:\Users\jgmeras\Documents\Python Scripts\6. CABANILLAS\Mturn\Muelle_optimo\implantaciones.xlsx"
    regex = r'\b([^.]+)\.'

    df = pd.read_excel(path, sheet_name="ImplantaciónPicking", header=0)
    df = df.iloc[2:, 3:5]

    # Detectar y asignar los encabezados
    new_headers = df.iloc[0]  # La primera fila del DataFrame recortado
    df = df[1:]  # Eliminar la primera fila ahora que se usa como encabezado
    df.columns = new_headers  # Asignar los nuevos encabezados
    df['Ubi'] = df['Picking Location'].str.extract(regex)

    return df
    

