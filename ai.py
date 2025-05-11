import copy
import random

class ThreeMensMorrisAI:
    def __init__(self, difficulty='medium'):
        self.difficulty = difficulty
        self.max_depth = {
            'easy': 2,
            'medium': 3,
            'hard': 4
        }.get(difficulty, 3)

    def evaluate_position(self, board, player):
        """
        Evaluate the current board position for the given player.
        Returns a score where higher is better for the player.
        """
        score = 0
        opponent = 3 - player  # 1 -> 2, 2 -> 1

        # Check for winning formations
        for row in range(3):
            # Horizontal
            if board[row][0] == board[row][1] == board[row][2] == player:
                score += 100
            elif board[row][0] == board[row][1] == board[row][2] == opponent:
                score -= 100

        for col in range(3):
            # Vertical
            if board[0][col] == board[1][col] == board[2][col] == player:
                score += 100
            elif board[0][col] == board[1][col] == board[2][col] == opponent:
                score -= 100

        # Diagonals
        if board[0][0] == board[1][1] == board[2][2] == player:
            score += 100
        elif board[0][0] == board[1][1] == board[2][2] == opponent:
            score -= 100

        if board[0][2] == board[1][1] == board[2][0] == player:
            score += 100
        elif board[0][2] == board[1][1] == board[2][0] == opponent:
            score -= 100

        # Center control
        if board[1][1] == player:
            score += 10
        elif board[1][1] == opponent:
            score -= 10

        # Mobility (number of valid moves)
        player_moves = self.count_valid_moves(board, player)
        opponent_moves = self.count_valid_moves(board, opponent)
        score += (player_moves - opponent_moves) * 5

        return score

    def count_valid_moves(self, board, player):
        """Count the number of valid moves available for a player."""
        count = 0
        for row in range(3):
            for col in range(3):
                if board[row][col] == player:
                    # Check all possible moves from this position
                    for dr in [-1, 0, 1]:
                        for dc in [-1, 0, 1]:
                            if dr == 0 and dc == 0:
                                continue
                            new_row, new_col = row + dr, col + dc
                            if (0 <= new_row < 3 and 0 <= new_col < 3 and 
                                board[new_row][new_col] == 0):
                                count += 1
        return count

    def get_valid_moves(self, board, player):
        """Get all valid moves for a player."""
        valid_moves = []
        for row in range(3):
            for col in range(3):
                if board[row][col] == player:
                    for dr in [-1, 0, 1]:
                        for dc in [-1, 0, 1]:
                            if dr == 0 and dc == 0:
                                continue
                            new_row, new_col = row + dr, col + dc
                            if (0 <= new_row < 3 and 0 <= new_col < 3 and 
                                board[new_row][new_col] == 0):
                                # Check if the move is valid according to game rules
                                # For diagonal moves, only allow if it's part of the X pattern
                                if dr != 0 and dc != 0:  # Diagonal move
                                    if (row == 0 and col == 0 and new_row == 1 and new_col == 1) or \
                                       (row == 0 and col == 2 and new_row == 1 and new_col == 1) or \
                                       (row == 2 and col == 0 and new_row == 1 and new_col == 1) or \
                                       (row == 2 and col == 2 and new_row == 1 and new_col == 1) or \
                                       (row == 1 and col == 1 and new_row == 0 and new_col == 0) or \
                                       (row == 1 and col == 1 and new_row == 0 and new_col == 2) or \
                                       (row == 1 and col == 1 and new_row == 2 and new_col == 0) or \
                                       (row == 1 and col == 1 and new_row == 2 and new_col == 2):
                                        valid_moves.append(((row, col), (new_row, new_col)))
                                else:  # Horizontal or vertical move
                                    valid_moves.append(((row, col), (new_row, new_col)))
        return valid_moves

    def minimax(self, board, depth, alpha, beta, maximizing_player, player):
        """Minimax algorithm with alpha-beta pruning."""
        if depth == 0:
            return self.evaluate_position(board, player)

        valid_moves = self.get_valid_moves(board, player if maximizing_player else 3 - player)
        
        if maximizing_player:
            max_eval = float('-inf')
            for (from_row, from_col), (to_row, to_col) in valid_moves:
                # Make move
                new_board = copy.deepcopy(board)
                new_board[to_row][to_col] = player
                new_board[from_row][from_col] = 0
                
                eval = self.minimax(new_board, depth - 1, alpha, beta, False, player)
                max_eval = max(max_eval, eval)
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break
            return max_eval
        else:
            min_eval = float('inf')
            for (from_row, from_col), (to_row, to_col) in valid_moves:
                # Make move
                new_board = copy.deepcopy(board)
                new_board[to_row][to_col] = 3 - player
                new_board[from_row][from_col] = 0
                
                eval = self.minimax(new_board, depth - 1, alpha, beta, True, player)
                min_eval = min(min_eval, eval)
                beta = min(beta, eval)
                if beta <= alpha:
                    break
            return min_eval

    def get_best_move(self, board, player):
        """Get the best move for the AI player."""
        valid_moves = self.get_valid_moves(board, player)
        if not valid_moves:
            return None

        best_move = None
        best_eval = float('-inf')
        alpha = float('-inf')
        beta = float('inf')

        for (from_row, from_col), (to_row, to_col) in valid_moves:
            # Make move
            new_board = copy.deepcopy(board)
            new_board[to_row][to_col] = player
            new_board[from_row][from_col] = 0
            
            eval = self.minimax(new_board, self.max_depth - 1, alpha, beta, False, player)
            
            if eval > best_eval:
                best_eval = eval
                best_move = ((from_row, from_col), (to_row, to_col))

        return best_move 