import random

def start_game():
    print("Welcome to the Text Adventure!")
    print("You are in a dark forest. You see a path leading north and a cave to the east.")
    choice = input("Do you go north or east? ").lower()

    if choice == "north":
        north_path()
    elif choice == "east":
        enter_cave()
    else:
        print("Invalid choice. You wander aimlessly and are eaten by a grue.")

def north_path():
    print("You follow the path north.")
    print("You encounter a friendly wizard who gives you a magic sword.")
    print("You continue north and reach a village.")
    print("Congratulations! You win!")

def enter_cave():
    print("You enter the dark cave.")
    print("A goblin jumps out and attacks you!")
    fight_goblin()

def fight_goblin():
    print("You have a 50% chance to win the fight.")
    if random.random() < 0.5:
        print("You defeat the goblin and find treasure!")
        print("Congratulations! You win!")
    else:
        print("The goblin defeats you.")
        print("Game Over.")

start_game()
