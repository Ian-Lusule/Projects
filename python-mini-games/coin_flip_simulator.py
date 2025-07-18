import random

def coin_flip():
    """Simulates a coin flip and prints the result."""
    result = random.choice(["Heads", "Tails"])
    print("The coin landed on:", result)

if __name__ == "__main__":
    coin_flip()

