import random

def play_round():
    user_choice = input("Choose rock, paper, or scissors: ").lower()
    while user_choice not in ["rock", "paper", "scissors"]:
        print("Invalid choice. Please try again.")
        user_choice = input("Choose rock, paper, or scissors: ").lower()

    computer_choice = random.choice(["rock", "paper", "scissors"])
    print(f"Computer chose: {computer_choice}")

    if user_choice == computer_choice:
        print("It's a tie!")
    elif (user_choice == "rock" and computer_choice == "scissors") or \
         (user_choice == "paper" and computer_choice == "rock") or \
         (user_choice == "scissors" and computer_choice == "paper"):
        print("You win!")
    else:
        print("You lose!")

def play_game():
    while True:
        play_round()
        play_again = input("Play again? (y/n): ").lower()
        if play_again != "y":
            break

if __name__ == "__main__":
    print("Welcome to Rock Paper Scissors!")
    play_game()

