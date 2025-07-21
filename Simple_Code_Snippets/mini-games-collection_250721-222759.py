```python
# Number guessing game
import random

def number_guessing_game():
    number = random.randint(1, 100)
    guess = 0
    tries = 0
    print("Welcome to the Number Guessing Game!")
    print("I'm thinking of a number between 1 and 100.")
    while guess != number:
        try:
            guess = int(input("Take a guess: "))
            tries += 1
            if guess < number:
                print("Too low!")
            elif guess > number:
                print("Too high!")
        except ValueError:
            print("Invalid input. Please enter a number.")
    print(f"Congratulations! You guessed the number in {tries} tries.")

# Simple calculator
def simple_calculator():
    num1 = float(input("Enter first number: "))
    op = input("Enter operator (+, -, *, /): ")
    num2 = float(input("Enter second number: "))

    if op == "+":
        print(num1 + num2)
    elif op == "-":
        print(num1 - num2)
    elif op == "*":
        print(num1 * num2)
    elif op == "/":
        if num2 == 0:
            print("Division by zero error!")
        else:
            print(num1 / num2)
    else:
        print("Invalid operator.")


# To-do list app
def to_do_list_app():
    tasks = []
    while True:
        print("\nTo-Do List App")
        print("1. Add task")
        print("2. View tasks")
        print("3. Remove task")
        print("4. Exit")

        choice = input("Enter your choice: ")

        if choice == "1":
            task = input("Enter task: ")
            tasks.append(task)
            print("Task added!")
        elif choice == "2":
            if not tasks:
                print("No tasks yet.")
            else:
                print("\nYour tasks:")
                for i, task in enumerate(tasks):
                    print(f"{i+1}. {task}")
        elif choice == "3":
            if not tasks:
                print("No tasks to remove.")
            else:
                print("\nYour tasks:")
                for i, task in enumerate(tasks):
                    print(f"{i+1}. {task}")
                try:
                    remove_index = int(input("Enter the number of the task to remove: ")) -1
                    if 0 <= remove_index < len(tasks):
                        removed_task = tasks.pop(remove_index)
                        print(f"Task '{removed_task}' removed.")
                    else:
                        print("Invalid task number.")
                except ValueError:
                    print("Invalid input.")

        elif choice == "4":
            print("Exiting...")
            break
        else:
            print("Invalid choice.")


# Run the games/app
number_guessing_game()
simple_calculator()
to_do_list_app()

```