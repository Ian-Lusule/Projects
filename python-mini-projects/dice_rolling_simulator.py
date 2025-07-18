import random

def roll_dice(num_dice, num_sides):
    """Simulates rolling multiple dice with a specified number of sides."""
    results = []
    for _ in range(num_dice):
        results.append(random.randint(1, num_sides))
    return results

def main():
    while True:
        try:
            num_dice = int(input("Enter the number of dice to roll: "))
            num_sides = int(input("Enter the number of sides on each die: "))
            if num_dice <= 0 or num_sides <= 0:
                print("Please enter positive integers for the number of dice and sides.")
                continue
            break
        except ValueError:
            print("Invalid input. Please enter integers only.")

    results = roll_dice(num_dice, num_sides)
    print("Results:", results)
    print("Total:", sum(results))

if __name__ == "__main__":
    main()
