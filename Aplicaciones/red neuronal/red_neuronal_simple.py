import tensorflow as tf
import numpy as np
import matplotlib.pyplot as plt

#F = C *1.8+32

celsius = np.array([-40, 10, 0, 8, 15, 22, 38, 45, 60], dtype=float)
fahreneit = np.array([-40, 14, 32, 46.4 , 59, 72, 100.4, 113, 140], dtype=float)

#capa = tf.keras.layers.Dense(units=1, input_shape=[1])
#modelo = tf.keras.Sequential([capa])

oculta1 = tf.keras.layers.Dense(units=3, input_shape=[1])
oculta2 = tf.keras.layers.Dense(units=3)
salida = tf.keras.layers.Dense(units=1)
modelo = tf.keras.Sequential([oculta1, oculta2, salida])

modelo.compile(
    optimizer=tf.keras.optimizers.Adam(0.1),
    loss = 'mean_squared_error'
)

print("[+] Comenzando entrenamiento...")
historial = modelo.fit(celsius, fahreneit, epochs=1000, verbose=False)
print("[+] Modelo entrenando")


plt.xlabel("# Epoca")
plt.ylabel("Magnitud de perdida")
plt.plot(historial.history["loss"])

print("[+] Predicción")
resultado_entrada = np.array([100.0])
resultado = modelo.predict(resultado_entrada)
print(" El resultado es {} F".format(resultado))

print("Variables internas del modelo")
#print(capa.get_weights())

print(oculta1.get_weights())
print(oculta2.get_weights())
print(salida.get_weights())