import pandas as pd

# Leer los archivos CSV
trp_to_mturn_path = 'TRP_TO_MTURN2024-07-03.csv'
resultado_path = '20240702resultado.csv'

trp_df = pd.read_csv(trp_to_mturn_path)
resultado_df = pd.read_csv(resultado_path)

# Juntar las columnas "Hora", "Tractora", y "PO" del archivo TRP_TO_MTURN2024-07-03.csv
trp_df_subset = trp_df[['Hora', 'Tractora', 'PO']]

# Convertir las columnas 'PO' y 'delivery' a strings
trp_df_subset['PO'] = trp_df_subset['PO'].astype(str)
resultado_df['delivery'] = resultado_df['delivery'].astype(str)

# Comparar la columna "PO" de TRP_TO_MTURN2024-07-03.csv con la columna "delivery" de 20240702resultado.csv
merged_df = pd.merge(trp_df_subset, resultado_df[['delivery', 'muelle']], left_on='PO', right_on='delivery', how='left')

# Eliminar la columna duplicada "delivery"
merged_df.drop(columns=['delivery'], inplace=True)

# Convertir la columna 'muelle' a entero, manejando NaN
merged_df['muelle'] = pd.to_numeric(merged_df['muelle'], errors='coerce').fillna(0).astype(int)

# Guardar el DataFrame resultante en un nuevo archivo CSV
output_path = 'merged_output.csv'
merged_df.to_csv(output_path, index=False)

print(f"Archivo guardado en {output_path}")
