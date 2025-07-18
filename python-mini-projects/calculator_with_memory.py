```python
memory = 0

def add(x, y):
    global memory
    memory = x + y
    return memory

def subtract(x, y):
    global memory
    memory = x - y
    return memory

def multiply(x, y):
    global memory
    memory = x * y
    return memory

def divide(x, y):
    global memory
    if y == 0:
        return "Division by zero!"
    memory = x / y
    return memory

print("Select operation:")
print("1.Add")
print("2.Subtract")
print("3.Multiply")
print("4.Divide")
print("5.Memory Recall")
print("6.Clear Memory")

while True:
    choice = input("Enter choice(1/2/3/4/5/6): ")

    if choice in ('1', '2', '3', '4'):
        try:
            num1 = float(input("Enter first number: "))
            num2 = float(input("Enter second number: "))
        except ValueError:
            print("Invalid input. Please enter numbers only.")
            continue

        if choice == '1':
            print(num1, "+", num2, "=", add(num1, num2))
        elif choice == '2':
            print(num1, "-", num2, "=", subtract(num1, num2))
        elif choice == '3':
            print(num1, "*", num2, "=", multiply(num1, num2))
        elif choice == '4':
            print(num1, "/", num2, "=", divide(num1, num2))

    elif choice == '5':
        print("Memory:", memory)

    elif choice == '6':
        memory = 0
        print("Memory cleared.")

    else:
        print("Invalid Input")

    another_calculation = input("Another calculation? (yes/no): ")
    if another_calculation.lower() != 'yes':
        break

```
