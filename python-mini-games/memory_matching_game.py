import random

def create_board(size):
    cards = list(range(1, size // 2 + 1)) * 2
    random.shuffle(cards)
    return [cards[i:i+size] for i in range(0, len(cards), size)]

def print_board(board, revealed):
    for row in board:
        row_str = ""
        for i, card in enumerate(row):
            if revealed[row.index(card)][i]:
                row_str += str(card).zfill(2) + " "
            else:
                row_str += "** "
        print(row_str)

def get_player_choice(board, revealed):
    while True:
        try:
            row = int(input("Enter row (1-based index): ")) - 1
            col = int(input("Enter column (1-based index): ")) - 1
            if 0 <= row < len(board) and 0 <= col < len(board[0]) and not revealed[row][col]:
                return row, col
            else:
                print("Invalid input. Try again.")
        except ValueError:
            print("Invalid input. Try again.")

def play_game():
    size = 4  # Adjust for board size (must be even)
    board = create_board(size)
    revealed = [[False for _ in row] for row in board]
    first_choice = None
    moves = 0
    while True:
        print_board(board, revealed)
        row, col = get_player_choice(board, revealed)
        revealed[row][col] = True
        if first_choice is None:
            first_choice = (row, col, board[row][col])
        else:
            moves += 1
            if board[row][col] == first_choice[2]:
                print("Match found!")
                first_choice = None
            else:
                print("No match.")
                input("Press Enter to continue...")
                revealed[first_choice[0]][first_choice[1]] = False
                revealed[row][col] = False
                first_choice = None
        if all(all(row) for row in revealed):
            print("Congratulations! You won in", moves, "moves!")
            break

if __name__ == "__main__":
    play_game()

