import random

questions = {
    "What is the capital of France?": "Paris",
    "What is the highest mountain in the world?": "Mount Everest",
    "What is the largest ocean in the world?": "Pacific Ocean",
    "What is the chemical symbol for water?": "H2O",
    "What is the name of Earth's only natural satellite?": "Moon"
}

score = 0
total_questions = len(questions)

print("Welcome to the Quiz Game!")

for question, answer in questions.items():
    user_answer = input(f"{question} ")
    if user_answer.lower() == answer.lower():
        print("Correct!")
        score += 1
    else:
        print(f"Incorrect. The answer is {answer}.")

print(f"\nYou got {score} out of {total_questions} questions correct.")
percentage = (score / total_questions) * 100
print(f"Your score is {percentage:.2f}%")
