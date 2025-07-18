import random

def show_intro():
    print("Welcome to the Text Adventure Game!")
    print("You are in a dark forest...")

def describe_location(location):
    if location == "forest":
        print("You are in a dark forest. Trees loom around you, their branches intertwining overhead.")
        print("A path leads north and a stream flows to the east.")
    elif location == "stream":
        print("You are beside a clear stream.  The water gurgles gently.")
        print("You can go back west.")
    elif location == "cave":
        print("You are in a dark cave.  You see a glimmer of light in the distance.")
        print("You can go back west.")
    elif location == "treasure":
        print("You found the treasure! You win!")
        exit()


def get_player_choice():
    print("\nWhat do you want to do?")
    print("1. Go North")
    print("2. Go East")
    print("3. Go West")
    choice = input("> ")
    return choice

def play_game():
    current_location = "forest"
    show_intro()

    while True:
        describe_location(current_location)
        choice = get_player_choice()

        if current_location == "forest":
            if choice == "1":
                current_location = "cave"
            elif choice == "2":
                current_location = "stream"
            else:
                print("Invalid choice.")
        elif current_location == "stream":
            if choice == "3":
                current_location = "forest"
            else:
                print("Invalid choice.")
        elif current_location == "cave":
            if choice == "3":
                current_location = "forest"
            elif choice == "1":
                current_location = "treasure"
            else:
                print("Invalid choice.")

play_game()
