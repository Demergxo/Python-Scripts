
from alive_progress import alive_bar
import time

from alive_progress import animations

bar = animations.bar_factory('😴', tip="😪", background='zZz', borders=('Durmiendo 👉 ->|','|<- Terminado 🤘'), errors=('<---👀', '💀'))


total = 10  # Total de iteraciones
i = 0

with alive_bar(total, title='Durmiendo', spinner ='twirls', bar = bar) as bar:
    while i < total:
        time.sleep(1)  # Simula un pequeño proceso para ver el progreso.
        
        bar()  # Actualiza la barra de progreso.
        i += 1  # Incrementa el contador.

