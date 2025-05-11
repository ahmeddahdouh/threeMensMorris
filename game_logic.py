from typing import List, Tuple, Dict

def create_valid_connections() -> Dict[Tuple[int, int], List[Tuple[int, int]]]:
    """
    Create a dictionary with all valid moves for each position
    """
    connections = {}
    BOARD_ROWS, BOARD_COLS = 3, 3

    # For each position on the board
    for row in range(BOARD_ROWS):
        for col in range(BOARD_COLS):
            connections[(row, col)] = []

            # Horizontal and vertical moves (always allowed to adjacent squares)
            # Up
            if row > 0:
                connections[(row, col)].append((row - 1, col))
            # Down
            if row < BOARD_ROWS - 1:
                connections[(row, col)].append((row + 1, col))
            # Left
            if col > 0:
                connections[(row, col)].append((row, col - 1))
            # Right
            if col < BOARD_COLS - 1:
                connections[(row, col)].append((row, col + 1))

            # Diagonal moves (only main diagonals "in X")
            # Top-left to bottom-right
            if (row == 0 and col == 0) or (row == 2 and col == 2):
                if (row == 0 and col == 0):
                    connections[(row, col)].append((1, 1))  # to center
                if (row == 2 and col == 2):
                    connections[(row, col)].append((1, 1))  # to center

            # Top-right to bottom-left
            if (row == 0 and col == 2) or (row == 2 and col == 0):
                if (row == 0 and col == 2):
                    connections[(row, col)].append((1, 1))  # to center
                if (row == 2 and col == 0):
                    connections[(row, col)].append((1, 1))  # to center

            # Center to all four corners
            if row == 1 and col == 1:
                connections[(row, col)].append((0, 0))  # top-left
                connections[(row, col)].append((0, 2))  # top-right
                connections[(row, col)].append((2, 0))  # bottom-left
                connections[(row, col)].append((2, 2))  # bottom-right

    return connections

def get_valid_moves(board: List[List[int]], row: int, col: int, valid_connections: Dict[Tuple[int, int], List[Tuple[int, int]]]) -> List[Tuple[int, int]]:
    """
    Get valid moves for a piece at the given position
    """
    valid = []
    possible_moves = valid_connections.get((row, col), [])
    
    # Filter to keep only empty squares
    for new_row, new_col in possible_moves:
        if board[new_row][new_col] == 0:
            valid.append((new_row, new_col))
    
    return valid

def is_winning_state(board: List[List[int]], player: int) -> bool:
    """
    Check if the current board state is a winning state for the given player
    """
    # Check rows
    for row in range(3):
        if all(board[row][col] == player for col in range(3)):
            return True

    # Check columns
    for col in range(3):
        if all(board[row][col] == player for row in range(3)):
            return True

    # Check diagonals
    if all(board[i][i] == player for i in range(3)):
        return True
    if all(board[i][2-i] == player for i in range(3)):
        return True

    return False 