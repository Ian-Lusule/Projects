```python
# python-mini-utilities/__tests__/test_calculator.py

import unittest
from python_mini_utilities.calculator import calculate

class TestCalculator(unittest.TestCase):
    """Tests for the basic calculator functions."""

    def test_addition(self):
        self.assertEqual(calculate(1, 2, '+'), 3)
        self.assertEqual(calculate(-5, 10, '+'), 5)
        self.assertEqual(calculate(0, 0, '+'), 0)

    def test_subtraction(self):
        self.assertEqual(calculate(5, 2, '-'), 3)
        self.assertEqual(calculate(-5, 10, '-'), -15)
        self.assertEqual(calculate(0, 0, '-'), 0)

    def test_multiplication(self):
        self.assertEqual(calculate(5, 2, '*'), 10)
        self.assertEqual(calculate(-5, 10, '*'), -50)
        self.assertEqual(calculate(0, 5, '*'), 0)
        self.assertEqual(calculate(5, 0, '*'), 0)
        self.assertEqual(calculate(0, 0, '*'), 0)


    def test_division(self):
        self.assertEqual(calculate(10, 2, '/'), 5)
        self.assertEqual(calculate(-10, 2, '/'), -5)
        self.assertEqual(calculate(10, -2, '/'), -5)
        self.assertEqual(calculate(10, 0, '/'), "Division by zero!") #Testing error handling

    def test_invalid_operator(self):
        with self.assertRaises(ValueError):
            calculate(5, 2, '%')  #Invalid operator


    def test_invalid_input(self):
        with self.assertRaises(TypeError):
            calculate("a", 2, '+') #Invalid input type
        with self.assertRaises(TypeError):
            calculate(5, "b", '+') #Invalid input type


if __name__ == '__main__':
    unittest.main()
```

To make this code runnable, you'll also need a `calculator.py` file in a `python_mini_utilities` directory (you'll need to create these directories).  Here's what `calculator.py` should contain:


```python
# python-mini-utilities/calculator.py

def calculate(num1, num2, operator):
    """Performs basic arithmetic operations.

    Args:
        num1: The first number.
        num2: The second number.
        operator: The operator (+, -, *, /).

    Returns:
        The result of the operation.  Returns an error message for division by zero.

    Raises:
        ValueError: If an invalid operator is provided.
        TypeError: if input is not a number.

    """
    if not isinstance(num1,(int,float)) or not isinstance(num2,(int,float)):
        raise TypeError("Inputs must be numbers.")

    if operator == '+':
        return num1 + num2
    elif operator == '-':
        return num1 - num2
    elif operator == '*':
        return num1 * num2
    elif operator == '/':
        if num2 == 0:
            return "Division by zero!"
        else:
            return num1 / num2
    else:
        raise ValueError("Invalid operator.")

```

Remember to run `pip install unittest` if you haven't already.  Then, from the directory containing `test_calculator.py`, you can run the tests using `python -m unittest test_calculator.py`.
