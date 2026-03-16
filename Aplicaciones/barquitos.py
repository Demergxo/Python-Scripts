import random
import math
import sys

def get_new_board():
    #crea un tablero de 60x15
    board = []
    for x in range(60): #la lista principal es de 60 listas
        board.append([])
        for y in range(15): #cada lista en la lista principal tiene 15 caracteres de un unico caracter
            if random.randint(0, 1) == 0:
                board[x].append('~')
            else:
                board[x].append('`')
    return board

def draw_board(board):
    tens_digits_line = '    '#Espacio inicial para los números abajo a la izquierda lado del tablero
    for i in range(1, 6):
        tens_digits_line += (' '*9) + str(i)
        
    #imprime los numeros en la parte superior del tablero
    print(tens_digits_line)
    print('   ' + ('0123456789' * 6))
    print()
    
    #imprime cada uno de las 15 líneas
    for row in range(15):
        if row < 10:
            extra_space = ' '
        else:
            extra_space= ''
    
    #crear la cadena para esta linea del tablero
        board_row = ''
        for column in range(60):
            board_row += board[column][row]
        
        print("{}{} {} {}".format(extra_space, row, board_row, row))
    
    #imprime los numeros en la parte baja
    print()
    print("   "+"0123456789" * 6)
    print(tens_digits_line)
    
def get_random_chests(num_chests):
    # crear estructura de coordenadas para los barcos con int x,y
    chests = []
    while len(chests) < num_chests:
        new_chest = [random.randint(0,59), random.randint(0,14)]
        if new_chest not in chests: #estar seguro que el barco no está aquí
            chests.append(new_chest)
    
    return chests

def is_on_board(x, y):
    #comprueba si las coordenadas son validas, si no, devuelve False
    
    return x >=0 and x <= 59 and y >= 0 and y <= 14

def make_move(board, chests, x, y):
    #cambia la structura de datos del tablero, eliminando el barco si lo encuentra
    #devuelve False si el movimiento es invalido
    #si no, devuelve la cadena del resultado del movimiento
    
    smallest_distance = 100 #cualquier barco tiene que estar más cerca de 100
    for cx, cy in chests:
        distance = math.sqrt((cx-x)*(cx-x) + (cy-y)* (cy-y))
        if distance < smallest_distance: #queremos el barco más cercano
            smallest_distance = distance
            
    smallest_distance = round(smallest_distance)
    
    if smallest_distance == 0:
        #xy es sobre el barco
        chests.remove([x,y])
        return "Has emcontrado un barco!!!"
    else:
        if smallest_distance < 10:
            board[x][y] = str(smallest_distance)
            return "Barco detectado a {} de distancia del tiro".format(smallest_distance)
        else:
            board[x][y] = "X"
            return "Agua..."
        
    


    