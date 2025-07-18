```python
"""
A simple calculator application.
"""

import operator

def calculate(num1, num2, operation):
    """
    Performs a calculation based on the provided numbers and operation.

    Args:
        num1: The first number.
        num2: The second number.
        operation: The operation to perform ('+', '-', '*', '/').

    Returns:
        The result of the calculation, or an error message if invalid input is provided.
    """

    operations = {
        '+': operator.add,
        '-': operator.sub,
        '*': operator.mul,
        '/': operator.truediv,
    }

    if operation not in operations:
        return "Invalid operation. Please use '+', '-', '*', or '/'."

    if operation == '/' and num2 == 0:
        return "Error: Division by zero."

    try:
        num1 = float(num1)
        num2 = float(num2)
        result = operations[operation](num1, num2)
        return result
    except ValueError:
        return "Invalid input. Please enter numbers only."


def main():
    """
    Gets user input and performs the calculation.
    """
    while True:
        try:
            num1 = input("Enter the first number: ")
            num2 = input("Enter the second number: ")
            operation = input("Enter the operation (+, -, *, /): ")

            result = calculate(num1, num2, operation)
            print("Result:", result)
            break  # Exit loop if calculation is successful

        except Exception as e:
            print(f"An error occurred: {e}")
            continue # Continue loop if an error occurs


if __name__ == "__main__":
    main()

```