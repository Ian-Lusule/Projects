import random

def calculate(num1, num2, operator):
    if operator == '+':
        return num1 + num2
    elif operator == '-':
        return num1 - num2
    elif operator == '*':
        return num1 * num2
    elif operator == '/':
        if num2 == 0:
            return "Division by zero!"
        return num1 / num2
    else:
        return "Invalid operator"

def calculator_game():
    score = 0
    num_questions = 5

    print("Welcome to the Calculator Game!")

    for _ in range(num_questions):
        num1 = random.randint(1, 10)
        num2 = random.randint(1, 10)
        operators = ['+', '-', '*', '/']
        operator = random.choice(operators)

        print(f"\nWhat is {num1} {operator} {num2}?")
        try:
            user_answer = float(input("Your answer: "))
            correct_answer = calculate(num1, num2, operator)
            if isinstance(correct_answer, str):
                print(correct_answer)
            elif abs(user_answer - correct_answer) < 1e-6:  # Account for floating-point precision
                print("Correct!")
                score += 1
            else:
                print(f"Incorrect. The answer is {correct_answer}")
        except ValueError:
            print("Invalid input. Please enter a number.")

    print(f"\nGame over! Your score: {score}/{num_questions}")

if __name__ == "__main__":
    calculator_game()
