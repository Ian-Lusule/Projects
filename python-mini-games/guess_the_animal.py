import random

animals = ["lion", "tiger", "bear", "elephant", "giraffe", "zebra", "monkey", "dog", "cat", "bird"]
secret_animal = random.choice(animals)
guesses_left = 20

print("Welcome to Guess the Animal!")
print("I'm thinking of an animal. You have 20 questions to guess it.")

while guesses_left > 0:
    print("\nGuesses left:", guesses_left)
    question = input("Ask a yes/no question: ")
    
    if "is it a" in question.lower() or "is it an" in question.lower():
        animal_guess = question.lower().split("is it a ")[-1].split("is it an ")[-1].strip()
        if animal_guess == secret_animal:
            print("Congratulations! You guessed it!")
            break
        else:
            guesses_left -=1
            print("Nope, try again.")
    elif "does it" in question.lower():
        answer = input("Is the answer yes or no? ").lower()
        if (answer == "yes" and "yes" in secret_animal) or (answer == "no" and "no" not in secret_animal):
            print("Correct!")
        else:
            guesses_left -= 1
            print("Incorrect.")
    else:
        print("Please ask a yes/no question.")
        guesses_left -=1

if guesses_left == 0:
    print("\nYou ran out of guesses. The animal was", secret_animal)

