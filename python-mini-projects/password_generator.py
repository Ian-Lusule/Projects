import random
import string

def generate_password(length=12, include_lowercase=True, include_uppercase=True, include_numbers=True, include_symbols=True):
    characters = ""
    if include_lowercase:
        characters += string.ascii_lowercase
    if include_uppercase:
        characters += string.ascii_uppercase
    if include_numbers:
        characters += string.digits
    if include_symbols:
        characters += string.punctuation

    if not characters:
        return "Please select at least one character type."

    password = ''.join(random.choice(characters) for i in range(length))
    return password

if __name__ == "__main__":
    length = int(input("Enter desired password length: "))
    lowercase = input("Include lowercase letters? (y/n): ").lower() == 'y'
    uppercase = input("Include uppercase letters? (y/n): ").lower() == 'y'
    numbers = input("Include numbers? (y/n): ").lower() == 'y'
    symbols = input("Include symbols? (y/n): ").lower() == 'y'

    password = generate_password(length, lowercase, uppercase, numbers, symbols)
    print("Generated password:", password)

