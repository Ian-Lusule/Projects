```python
"""
password_generator.py: Generates random passwords of specified length and complexity.
"""
import random
import string

def generate_password(length=12, include_uppercase=True, include_lowercase=True, 
                      include_numbers=True, include_symbols=True):
    """Generates a random password.

    Args:
        length: The desired length of the password (default is 12).  Must be a positive integer.
        include_uppercase: Whether to include uppercase letters (default is True).
        include_lowercase: Whether to include lowercase letters (default is True).
        include_numbers: Whether to include numbers (default is True).
        include_symbols: Whether to include symbols (default is True).

    Returns:
        A randomly generated password string.  Returns None if invalid parameters are provided.

    Raises:
        ValueError: If length is not a positive integer or if no character sets are selected.

    """
    if not isinstance(length, int) or length <= 0:
        raise ValueError("Password length must be a positive integer.")

    if not any([include_uppercase, include_lowercase, include_numbers, include_symbols]):
        raise ValueError("At least one character set must be selected.")

    characters = ""
    if include_uppercase:
        characters += string.ascii_uppercase
    if include_lowercase:
        characters += string.ascii_lowercase
    if include_numbers:
        characters += string.digits
    if include_symbols:
        characters += string.punctuation

    password = ''.join(random.choice(characters) for i in range(length))
    return password


def main():
    """Gets user input and generates a password."""
    try:
        length = int(input("Enter desired password length (default is 12): ") or "12")
        include_uppercase = input("Include uppercase letters? (y/n, default is y): ").lower() != 'n'
        include_lowercase = input("Include lowercase letters? (y/n, default is y): ").lower() != 'n'
        include_numbers = input("Include numbers? (y/n, default is y): ").lower() != 'n'
        include_symbols = input("Include symbols? (y/n, default is y): ").lower() != 'n'

        password = generate_password(length, include_uppercase, include_lowercase, include_numbers, include_symbols)
        print("\nGenerated password:", password)

    except ValueError as e:
        print("Error:", e)
    except Exception as e:
        print("An unexpected error occurred:", e)


if __name__ == "__main__":
    main()

```