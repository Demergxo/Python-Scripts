import funciones as f
import time as t
import pandas as pd

indice = {
    "Dogs": [],
    "Cats": [],
    "Others": [],
    "Consumables": [],
    "Out of family": [],
}

t.sleep(5)
resol = {
    "" : "",
}
indice = f.leer_master_data(indice)
delivery = f.separar_por_delivery()
#archivo_implantaciones_df = f.leer_archivo_implantaciones()
la_por_ubi = f.catalogar_delivery_skus(delivery) #type: ignore




# for delivery_id, items_quantities in delivery.items():
#     total = 0
#     print(f"Delivery ID: {delivery_id}")
#     for item, quantity in items_quantities:
#         vol = f.calcular_vol(item, quantity)
#         total += vol
#         print(f"  Item: {item}, Quantity Expected: {quantity}, vol: {vol:.2f} m3")
#     print(f"Vol total: {total:.2f} m3")

sep = f.catalogar_delivery_skus(delivery, indice)

for delivery_id, details in sep.items():
    print(f"La delivery [{delivery_id}] tiene la mayor parte de [{details['Majority Family']}] con un [{details['Majority Percentage']:.2f}%]")


