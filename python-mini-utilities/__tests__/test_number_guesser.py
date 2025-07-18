```python
import random
import unittest

# number_guesser.py

def guess_the_number(max_number=100):
    """Plays a number guessing game with the user.

    Args:
        max_number: The upper limit for the random number (inclusive). Defaults to 100.

    Returns:
        The number of guesses it took the user to guess the number.  Returns -1 if invalid input is provided.
    """
    if not isinstance(max_number, int) or max_number <= 0:
        print("Invalid max_number. Please provide a positive integer.")
        return -1

    secret_number = random.randint(1, max_number)
    guesses_taken = 0
    while True:
        try:
            guess = int(input(f"Guess a number between 1 and {max_number}: "))
            guesses_taken += 1
            if guess < secret_number:
                print("Too low!")
            elif guess > secret_number:
                print("Too high!")
            else:
                print(f"Congratulations! You guessed the number in {guesses_taken} tries.")
                return guesses_taken
        except ValueError:
            print("Invalid input. Please enter a number.")


# test_number_guesser.py

class TestNumberGuesser(unittest.TestCase):
    def test_valid_guess(self):
        # Mocking user input for testing purposes.  In a real scenario, this would interact with the user.
        with unittest.mock.patch('builtins.input', side_effect=[50, 60, 55, 58, 57]):
            self.assertEqual(guess_the_number(100), 5)

    def test_invalid_max_number(self):
        self.assertEqual(guess_the_number(-10), -1)  #Negative number
        self.assertEqual(guess_the_number(0), -1) #Zero
        self.assertEqual(guess_the_number(3.14), -1) #Float

    def test_invalid_input(self):
        # Mocking invalid user input
        with unittest.mock.patch('builtins.input', side_effect=["abc", "100"]):
            self.assertEqual(guess_the_number(100), 2) #Should still run after the invalid input


if __name__ == '__main__':
    unittest.main()

```