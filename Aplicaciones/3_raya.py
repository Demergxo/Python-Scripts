import random

def draw_board(board):
    print(board[6] + '|'+ board[7]+ '|' + board[8])
    print('-+-+-')
    print(board[3] + '|'+ board[4]+ '|' + board[5])
    print('-+-+-')
    print(board[0] + '|'+ board[1]+ '|' + board[2])


def get_player_move(board):
    while True:
        print("Cual es tu siguiente movimiento? (1-9)")
        move = input()
        if move.isdigit():  # Verifica si la entrada es un dígito
            move = int(move) - 1  # Ajusta el movimiento para que sea un índice válido en el tablero
            if 0 <= move <= 8 and is_space_free(board, move):
                return move
        print("Por favor, ingresa un número válido (1-9).")


def is_space_free(board, move):
    return board[move] == ' '


print("    BIENVENIDO A 2 EN RAYA")
print("*"*32)

while True:
    the_board = [' '] * 9  # Inicializa el tablero con espacios en blanco
    player_letter, computer_letter = input_player_letter()
    turn = who_goes_first()
    print("El turno {} va primero".format(turn))
    game_is_playing = True

    while game_is_playing:
        if turn == "Jugador":
            draw_board(the_board)
            move = get_player_move(the_board)
            the_board[move] = player_letter  # Actualiza el tablero con el movimiento del jugador

            if is_winner(the_board, player_letter):
                draw_board(the_board)
                print("¡Ole! ¡Has ganado!")
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
            the_board[move] = computer_letter  # Actualiza el tablero con el movimiento de la computadora

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
    if input().lower() != "s":
        break
