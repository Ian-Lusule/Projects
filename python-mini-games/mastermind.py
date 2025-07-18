import random

def generate_code(length=4, digits=True):
    if digits:
        return ''.join(random.choices('0123456789', k=length))
    else:
        return ''.join(random.choices('ABCDEF', k=length))

def get_guess(length):
    while True:
        guess = input(f"Enter your {length}-digit guess: ").upper()
        if len(guess) != length or not guess.isalnum():
            print("Invalid guess. Please try again.")
        else:
            return guess

def check_guess(secret_code, guess):
    black_pegs = 0
    white_pegs = 0
    secret_list = list(secret_code)
    guess_list = list(guess)

    for i in range(len(secret_code)):
        if guess_list[i] == secret_list[i]:
            black_pegs += 1
            secret_list[i] = ''
            guess_list[i] = ''

    for i in range(len(guess_list)):
        if guess_list[i] != '' and guess_list[i] in secret_list:
            white_pegs += 1
            secret_list[secret_list.index(guess_list[i])] = ''

    return black_pegs, white_pegs

def play_mastermind(code_length=4, use_digits=True):
    secret_code = generate_code(code_length, use_digits)
    guesses_left = 10

    print("Welcome to Mastermind!")
    if use_digits:
        print(f"I've generated a {code_length}-digit code using numbers 0-9.")
    else:
        print(f"I've generated a {code_length}-letter code using letters A-F.")

    while guesses_left > 0:
        print(f"\nYou have {guesses_left} guesses left.")
        guess = get_guess(code_length)
        black, white = check_guess(secret_code, guess)
        print(f"Black pegs: {black}, White pegs: {white}")

        if black == code_length:
            print(f"Congratulations! You cracked the code: {secret_code}")
            return

        guesses_left -= 1

    print(f"You ran out of guesses. The code was: {secret_code}")

if __name__ == "__main__":
    play_mastermind()

