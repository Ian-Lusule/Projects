import random

def roll_dice(num_dice, num_sides):
    results = []
    for _ in range(num_dice):
        results.append(random.randint(1, num_sides))
    return results

def main():
    num_dice = int(input("Enter the number of dice: "))
    num_sides = int(input("Enter the number of sides per die: "))

    results = roll_dice(num_dice, num_sides)
    print("Results:", results)
    print("Total:", sum(results))

if __name__ == "__main__":
    main()
