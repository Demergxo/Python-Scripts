def consultar_vol(la):
    import pandas as pd
    import os
    directory = os.getcwd()
    columna = 8
    path = os.path.join(directory,"6. CABANILLAS", "Mturn", "Muelle_optimo", "Master_data.xlsx")
    
    df =pd.read_excel(path)
    filtro = df['Articulo'] == la
    
    
    # Verificar si el valor 'la' se encuentra en la columna 'Articulo'
    if filtro.any():
        # Devolver la fila correspondiente al valor 'la'
        fila = df[filtro].iloc[0]
        valor_columna = fila[columna]
        return valor_columna
    else:
        # Si el valor 'la' no se encuentra, devolver None
        return None
        
            
