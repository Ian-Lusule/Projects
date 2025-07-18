import random

questions = {
    "What is the capital of France?": "Paris",
    "What is the highest mountain in the world?": "Mount Everest",
    "What is the largest ocean?": "Pacific Ocean",
    "What is the chemical symbol for water?": "H2O",
    "What is the name of Earth's only natural satellite?": "Moon"
}

score = 0
num_questions = len(questions)

print("Welcome to the Quiz Game!")

for question, answer in questions.items():
    user_answer = input(f"{question} ").lower()
    if user_answer == answer.lower():
        print("Correct!")
        score += 1
    else:
        print(f"Incorrect. The answer is {answer}.")

print(f"\nYou got {score} out of {num_questions} questions correct.")
percentage = (score / num_questions) * 100
print(f"Your score is {percentage:.2f}%")

if percentage >= 80:
    print("Excellent!")
elif percentage >= 60:
    print("Good job!")
else:
    print("Keep practicing!")
