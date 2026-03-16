import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error
from sklearn.impute import SimpleImputer

# Cargar los datos desde Excel
file_path = r"C:\Users\jgmeras\Downloads\prueba_predi.xlsx" 
data = pd.read_excel(file_path)

# Limpiar nombres de columnas si es necesario
data.columns = data.columns.str.strip()

# Definir las características (features) y el objetivo (target)
features = [
    "Prepared Qty 1D",
    "Prepared Qty 1W",
    "Prepared Qty 2W",
    "Prepared Qty 1M",
    "Prepared Qty 3M",
    "Prepared Qty 6M",
    "Prepared Qty 1Y"
]

# Imputar valores faltantes
imputer = SimpleImputer(strategy="mean")
X = imputer.fit_transform(data[features])  # Rellenar NaN en las características
y = data["Average"].fillna(data["Average"].mean())  # Rellenar NaN en el target

# Dividir los datos en conjuntos de entrenamiento y prueba
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Crear y entrenar un modelo de regresión
model = RandomForestRegressor(random_state=42)
model.fit(X_train, y_train)

# Hacer predicciones para todos los datos
data["Predicted_Average"] = model.predict(X)

# Asociar las predicciones con los ítems
resultados = data[["Item", "Average", "Predicted_Average"]]

# Ordenar de mayor a menor salida predicha
resultados = resultados.sort_values(by="Predicted_Average", ascending=False)

# Exportar a un archivo CSV
output_path = r"C:\Users\jgmeras\Downloads\predicciones_ordenadas.csv" 
resultados.to_csv(output_path, index=False)

print(f"Archivo exportado a {output_path}")
