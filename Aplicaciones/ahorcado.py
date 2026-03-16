import random

HANGMAN_PICS = ['''
 +---+
     |
     |
     |
    ===''', '''
 +---+
 O   |
     |
     |
    ===''','''
 +---+
 O   |
 |   |
 .   |
    ===''', '''
 +---+
 O   |
/|   |
     |
    ===''', '''
 +---+
 O   |
/|\  |
     |
    ===''', '''
 +---+
 O   |
/|\  |
/    |
    ===''', '''
 +---+
 O   |
/|\  |
/ \  |
    ===''', '''
     +---+
[O   |
/|\  |
/ \  |
    ===''', '''
 +---+
[O]  |
/|\  |
/ \  |
    ===''']

words = "mosca gato perro leon pajaro raton dos mesa coche robot jirafa monitor ventana lombriz elefante columna hormiga chichon hurraca amigo lapiz".split()

def get_random_word(wordlist):
    word_index = random.randint(0, len(wordlist)-1)
    return wordlist[word_index]

def display_board(missed_letters, correct_letters, secret_word):
    print(HANGMAN_PICS[len(missed_letters)])
    print("")
    
    print("Letras fallidas: ", end=" " )
    for letter in missed_letters:
        print(letter, end=" ")
    print("")
    
    blanks = "_" * len(secret_word)
    
    for i in range(len(secret_word)):
        if secret_word[i] in correct_letters:
            blanks = blanks[:i] + secret_word[i] + blanks[i+1:]
            
    for letter in blanks:
        print(letter, end=" ")
    print("")
    
def get_guess(alredy_guessed):
    while True:
        print("Introduzca una letra:")
        guess = input()
        guess = guess.lower()
        if len(guess) != 1:
            print("Una sola letra a la vez!!!")
            
        elif guess in alredy_guessed:
            print("Ya ha introducida esa letra, introduzca una nueva.")
            
        elif guess not in "abcdefghijklmnñopqrstuvwxyz":
            print("Introduzca una LETRA!!!")
            
        else:
            return guess
        
def play_again():
    print("¿Quiere volver a jugar? (Si o No)")
    return input().lower().startswith("s")

print("  A H O R C A D O")
print("*"*19)
print("\n"*2)

missed_letters = ""
correct_letters = ""

secret_word = get_random_word(words)
game_is_done = False

while True:
    display_board(missed_letters, correct_letters, secret_word)
    
    guess = get_guess(missed_letters + correct_letters )
    
    if guess in secret_word:
        correct_letters = correct_letters + guess
        
        found_all_letters = True
        for i in range(len(secret_word)):
            if secret_word[i] not in  correct_letters:
                found_all_letters = False
                break
        if found_all_letters:
            print("Exacto! la palabra secreta era: "+ secret_word)
            print("Ganaste!!!")
            game_is_done = True
            
    else:
        missed_letters = missed_letters + guess
        
        if len(missed_letters) == len(HANGMAN_PICS)-1:
            display_board(missed_letters=missed_letters, correct_letters=correct_letters, secret_word=secret_word)
            print("Te has pasado de intentos!!\nHas conseguido: " + str(len(correct_letters)) + "aciertos y "+ str(len(missed_letters))+ "fallos" )
            print("La palabra secreta era: " + secret_word.upper())
            game_is_done = True
            
    if game_is_done:
        if play_again():
            missed_letters = ""
            correct_letters = ""
            game_is_done = False
            secret_word = get_random_word(words)
        else:
            break