import random

def draw_board(board):
    
    print(board[7] + '|'+ board[8]+ '|' + board[9])
    print('-+-+-')
    print(board[4] + '|'+ board[5]+ '|' + board[6])
    print('-+-+-')
    print(board[1] + '|'+ board[2]+ '|' + board[3])
    
    
def input_player_letter():
    letter = ''
    while not (letter == 'X' or letter == 'O'):
        print("Quieres ser X o O? (X/O)")
        letter = input().upper()
        
        if letter == "X":
            return ["X", "O"]
        else:
            return ["O", "X"]
        
def who_goes_first():
    if random.randint(0, 1) == 0:
        return "Computadora"
    else:
        return "Jugador"
    
def make_move(board, letter, move):
    board[move]=letter
    
def is_winner(board, letter):
    
    return ((board[7] == letter and board[8] == letter and board[9] == letter) or #linea h
            (board[4] == letter and board[5] == letter and board[6] == letter) or #linea h
            (board[1] == letter and board[2] == letter and board[3] == letter) or #linea h
            (board[7] == letter and board[4] == letter and board[1] == letter) or #linea v
            (board[8] == letter and board[5] == letter and board[2] == letter) or #linea v
            (board[9] == letter and board[6] == letter and board[3] == letter) or #linea v
            (board[7] == letter and board[5] == letter and board[3] == letter) or #diagonal
            (board[1] == letter and board[5] == letter and board[9] == letter)) #diagonal
    
def get_board_copy(board):
    boardcopy = []
    for i in board:
        boardcopy.append(i)
    return boardcopy

def is_space_free(board, move):
    return board[move] == None

def get_player_move(board):
    move = ' '
    while move not in '1 2 3 4 5 6 7 8 9'.split() or not is_space_free(board, move):
        print("Cual es tu siguiente movimiento? (1-9)")
        move = input()
    return int(move)

def random_move_from_list(board, moves_list):
    possible_moves = []
    for i in moves_list:
        if is_space_free(board, i):
            possible_moves.append(i)
        if len(possible_moves) != 0:
            return random.choice(possible_moves)
        else:
            return None
        
def get_computer_move(board, computer_letter):
    if computer_letter == "X":
        player_letter = "O"
    else:
        player_letter = "X"
        
    for i in range(1,10):
        boardcopy =get_board_copy(board)
        if is_space_free(boardcopy, i):
            make_move(boardcopy, computer_letter,i)
            if is_winner(boardcopy, computer_letter):
                return i
            
    for i in range(1,10):
        boardcopy =get_board_copy(board)
        if is_space_free(boardcopy, i):
            make_move(boardcopy, player_letter,i)
            if is_winner(boardcopy, player_letter):
                return i
            
    move = random_move_from_list(board, [1, 3, 7, 9])
    if move != None:
        return move
    
    if is_space_free(board, 5):
        return 5
    
    return random_move_from_list(board, [2, 4, 6, 8])

def is_board_full(board):
    for i in range(1, 10):
        if is_space_free(board, i):
            return False
    return True


print("    BIENVENIDO A 3 EN RAYA")
print("*"*32)

while True:
    the_board=list(' ' * 10)
    player_letter, computer_letter = input_player_letter()
    turn = who_goes_first()
    print("El turno {} va primero".format(turn))
    game_is_playing = True
    
    while game_is_playing:
        if turn == "Jugador":
            draw_board(the_board)
            move = get_player_move(the_board)
            make_move(the_board, player_letter, move)
            
            if is_winner(the_board, player_letter):
                draw_board(the_board)
                print("Oleee!!! Has ganado!!!")
                game_is_playing = False
            else:
                if is_board_full(the_board):
                    draw_board(the_board)
                    print("El juego acaba en empate")
                    game_is_playing = False
                else:
                    turn = "Computadora"
        else:
            
            move = get_computer_move(the_board, computer_letter)
            make_move(the_board, computer_letter, move)
            
            if is_winner(the_board, computer_letter):
                draw_board(the_board)
                print("La Computadora te ha ganado...")
                game_is_playing = False
            else:
                if is_board_full(the_board):
                    draw_board(the_board)
                    print("El juego acaba en empate")
                    game_is_playing = False
                else:
                    turn = "Jugador"
        print("¿Quieres otra partida? (S/N)")
        if not input().lower().startswith("y"):
            break

                    