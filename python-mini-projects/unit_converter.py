```python
def convert_temperature(value, unit_from, unit_to):
    """Converts temperature between Celsius, Fahrenheit, and Kelvin."""
    if unit_from == "celsius":
        if unit_to == "fahrenheit":
            return (value * 9/5) + 32
        elif unit_to == "kelvin":
            return value + 273.15
        else:
            return value
    elif unit_from == "fahrenheit":
        if unit_to == "celsius":
            return (value - 32) * 5/9
        elif unit_to == "kelvin":
            return (value - 32) * 5/9 + 273.15
        else:
            return value
    elif unit_from == "kelvin":
        if unit_to == "celsius":
            return value - 273.15
        elif unit_to == "fahrenheit":
            return (value - 273.15) * 9/5 + 32
        else:
            return value
    else:
        return "Invalid unit"


def convert_length(value, unit_from, unit_to):
    """Converts length between meters, centimeters, kilometers, inches, feet, and miles."""
    meters = 0
    if unit_from == "meters":
        meters = value
    elif unit_from == "centimeters":
        meters = value / 100
    elif unit_from == "kilometers":
        meters = value * 1000
    elif unit_from == "inches":
        meters = value * 0.0254
    elif unit_from == "feet":
        meters = value * 0.3048
    elif unit_from == "miles":
        meters = value * 1609.34
    else:
        return "Invalid unit"

    if unit_to == "meters":
        return meters
    elif unit_to == "centimeters":
        return meters * 100
    elif unit_to == "kilometers":
        return meters / 1000
    elif unit_to == "inches":
        return meters / 0.0254
    elif unit_to == "feet":
        return meters / 0.3048
    elif unit_to == "miles":
        return meters / 1609.34
    else:
        return "Invalid unit"


def convert_weight(value, unit_from, unit_to):
    """Converts weight between kilograms, grams, pounds, and ounces."""
    kilograms = 0
    if unit_from == "kilograms":
        kilograms = value
    elif unit_from == "grams":
        kilograms = value / 1000
    elif unit_from == "pounds":
        kilograms = value * 0.453592
    elif unit_from == "ounces":
        kilograms = value * 0.0283495
    else:
        return "Invalid unit"

    if unit_to == "kilograms":
        return kilograms
    elif unit_to == "grams":
        return kilograms * 1000
    elif unit_to == "pounds":
        return kilograms / 0.453592
    elif unit_to == "ounces":
        return kilograms / 0.0283495
    else:
        return "Invalid unit"


if __name__ == "__main__":
    print("Select conversion type:")
    print("1. Temperature")
    print("2. Length")
    print("3. Weight")

    choice = input("Enter your choice (1-3): ")

    if choice == "1":
        value = float(input("Enter value: "))
        unit_from = input("Enter unit (celsius, fahrenheit, kelvin): ").lower()
        unit_to = input("Enter target unit (celsius, fahrenheit, kelvin): ").lower()
        result = convert_temperature(value, unit_from, unit_to)
        print(f"Result: {result}")
    elif choice == "2":
        value = float(input("Enter value: "))
        unit_from = input("Enter unit (meters, centimeters, kilometers, inches, feet, miles): ").lower()
        unit_to = input("Enter target unit (meters, centimeters, kilometers, inches, feet, miles): ").lower()
        result = convert_length(value, unit_from, unit_to)
        print(f"Result: {result}")
    elif choice == "3":
        value = float(input("Enter value: "))
        unit_from = input("Enter unit (kilograms, grams, pounds, ounces): ").lower()
        unit_to = input("Enter target unit (kilograms, grams, pounds, ounces): ").lower()
        result = convert_weight(value, unit_from, unit_to)
        print(f"Result: {result}")
    else:
        print("Invalid choice")

```
