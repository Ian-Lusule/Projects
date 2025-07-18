import random
import time

colors = ["Red", "Green", "Blue", "Yellow"]
sequence = []
player_input = []

def generate_sequence(length):
    for _ in range(length):
        sequence.append(random.choice(colors))

def get_player_input(length):
    print("Enter the sequence:")
    for i in range(length):
        while True:
            try:
                color = input(f"Color {i+1}: ").title()
                if color in colors:
                    player_input.append(color)
                    break
                else:
                    print("Invalid color. Please choose from Red, Green, Blue, Yellow.")
            except:
                print("Invalid input. Please enter a color.")


def check_sequence():
    if sequence == player_input:
        return True
    else:
        return False

def play_game():
    level = 1
    while True:
        print(f"\nLevel: {level}")
        generate_sequence(level)
        print("Sequence:")
        for color in sequence:
            print(color, end=" ")
            time.sleep(1)
        print("\n")
        player_input.clear()
        get_player_input(level)
        if check_sequence():
            print("Correct! You advance to the next level.")
            level += 1
        else:
            print("Incorrect sequence. Game Over!")
            break

if __name__ == "__main__":
    print("Welcome to Simon Says!")
    play_game()

