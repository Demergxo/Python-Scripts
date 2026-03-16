# import time

# def mide_tiempo(func):
#     def wrapper(*args, **kwargs):
#         inicio = time.time()
#         resultado = func(*args, **kwargs)
#         fin = time.time()
#         print(f"La función {func.__name__} tardó {fin - inicio} segundos")
#         return resultado
#     return wrapper

# @mide_tiempo
# def repite_funcion(funcion, entrada):
#     return [funcion(entrada) for i in range(10000000)]

# def opera1(operador, a, b):
#     if operador == 'suma':
#         return a + b
#     elif operador == 'resta':
#         return a - b
#     elif operador == 'multiplica':
#         return a * b
#     elif operador == 'divide':
#         return a / b
#     else:
#         return "Operador inválido"
    
# def opera2(operador, a, b):
#     return {
#         'suma': a + b,
#         'resta': a - b,
#         'multiplica': a * b,
#         'divide': a / b if b != 0 else None
#     }.get(operador, lambda: None)
    
    
# # print(opera1('suma', 2, 3))
# # print(opera2('suma', 2, 3))

# tabla_switch = {
#         '0': '000',
#         '1': '001',
#         '2': '010',
#         '3': '011',
#         '4': '100',
#         '5': '101',
#         '6': '110',
#         '7': '111',
#     }
# def usa_switch(decimal):
#     return tabla_switch.get(decimal, "NA")

# def usa_if(decimal):
#     if decimal == '0':
#         return "000"
#     elif decimal == '1':
#         return "001"
#     elif decimal == '2':
#         return "010"
#     elif decimal == '3':
#         return "011"
#     elif decimal == '4':
#         return "100"
#     elif decimal == '5':
#         return "101"
#     elif decimal == '6':
#         return "110"
#     elif decimal == '7':
#         return "111"
#     else:
#         return "NA"


# print("\nUsa if:\n")
# for i in range(10):
#     repite_funcion(usa_if, str(i))
    
    
# print("\nUsa switch:\n")
# for i in range(10):
#     repite_funcion(usa_switch, str(i))

a = [1, 2, 3, 4]
b = ['uno', 'dos', 'tres', 'cuatro']

c= zip(a, b)

print(list(c))

esp = {'1': 'Uno', '2': 'Dos', '3': 'Tres'}
eng = {'1': 'One', '2': 'Two', '3': 'Three'}

for (k1, v1), (k2, v2) in zip(esp.items(), eng.items()):
    print(k1, v1, v2)



vuelta = 0
total =5

