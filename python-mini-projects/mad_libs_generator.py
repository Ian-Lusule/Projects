import random

def read_template(filepath):
    try:
        with open(filepath, 'r') as file:
            template = file.read()
        return template
    except FileNotFoundError:
        return None

def get_user_input(parts_of_speech):
    inputs = {}
    for pos in parts_of_speech:
        while True:
            user_input = input(f"Enter a {pos}: ")
            if user_input:
                inputs[pos] = user_input
                break
            else:
                print("Please enter a valid input.")
    return inputs

def fill_template(template, user_inputs):
    for pos, word in user_inputs.items():
        template = template.replace(f"{{{pos}}}", word)
    return template

def main():
    filepath = "madlib_template.txt"  # Replace with your template file
    template = read_template(filepath)

    if template:
        parts_of_speech = {
            "adjective": 1,
            "noun": 2,
            "verb": 1,
            "adverb": 1,
            # Add more parts of speech as needed
        }

        user_inputs = get_user_input(parts_of_speech)
        filled_template = fill_template(template, user_inputs)
        print("\nYour Mad Libs story:\n")
        print(filled_template)
    else:
        print(f"Error: Could not find template file at {filepath}")

if __name__ == "__main__":
    main()
