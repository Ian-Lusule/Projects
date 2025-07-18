import random

responses = {
    "greeting": ["Hello!", "Hi there!", "Hey!", "Greetings!"],
    "farewell": ["Goodbye!", "See you later!", "Farewell!", "Take care!"],
    "default": ["I'm not sure I understand.", "Can you rephrase that?", "I'm still learning..."]
}

def get_response(user_input):
    user_input = user_input.lower()
    if "hello" in user_input or "hi" in user_input:
        return random.choice(responses["greeting"])
    elif "bye" in user_input or "goodbye" in user_input:
        return random.choice(responses["farewell"])
    else:
        return random.choice(responses["default"])

def main():
    print("Simple Chatbot")
    print("Type 'bye' to exit.")

    while True:
        user_input = input("You: ")
        if user_input.lower() == "bye":
            print(get_response(user_input))
            break
        print("Chatbot:", get_response(user_input))

if __name__ == "__main__":
    main()
