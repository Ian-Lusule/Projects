import random

def generate_word_search(words, grid_size=10):
    grid = [['' for _ in range(grid_size)] for _ in range(grid_size)]
    
    def place_word(word, direction):
        row, col = random.randint(0, grid_size - 1), random.randint(0, grid_size - 1)
        
        if direction == 'horizontal':
            if col + len(word) > grid_size:
                return False
            for i, letter in enumerate(word):
                if grid[row][col + i] != '' and grid[row][col + i] != letter:
                    return False
            for i, letter in enumerate(word):
                grid[row][col + i] = letter
            return True
        elif direction == 'vertical':
            if row + len(word) > grid_size:
                return False
            for i, letter in enumerate(word):
                if grid[row + i][col] != '' and grid[row + i][col] != letter:
                    return False
            for i, letter in enumerate(word):
                grid[row + i][col] = letter
            return True
        elif direction == 'diagonal_down_right':
            if row + len(word) > grid_size or col + len(word) > grid_size:
                return False
            for i, letter in enumerate(word):
                if grid[row + i][col + i] != '' and grid[row + i][col + i] != letter:
                    return False
            for i, letter in enumerate(word):
                grid[row + i][col + i] = letter
            return True
        elif direction == 'diagonal_down_left':
            if row + len(word) > grid_size or col - len(word) +1 < 0:
                return False
            for i, letter in enumerate(word):
                if grid[row + i][col - i] != '' and grid[row + i][col - i] != letter:
                    return False
            for i, letter in enumerate(word):
                grid[row + i][col - i] = letter
            return True
        return False

    directions = ['horizontal', 'vertical', 'diagonal_down_right', 'diagonal_down_left']
    for word in words:
        placed = False
        for _ in range(100): # Try multiple times to place each word
            direction = random.choice(directions)
            if place_word(word.upper(), direction):
                placed = True
                break
        if not placed:
            print(f"Could not place word: {word}")

    for row in grid:
        for i in range(len(row)):
            if row[i] == '':
                row[i] = chr(random.randint(65, 90)) # Fill empty spaces with random letters

    return grid

def print_grid(grid):
    for row in grid:
        print(' '.join(row))

words = ["PYTHON", "JAVA", "CPLUSPLUS", "JAVASCRIPT", "KOTLIN", "SWIFT", "GO", "RUBY", "PHP", "PERL"]
grid = generate_word_search(words)
print_grid(grid)

